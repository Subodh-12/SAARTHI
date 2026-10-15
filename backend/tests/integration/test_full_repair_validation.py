"""End-to-end validation test suite verifying application repair:
- Authentication & Bearer lifecycle (activation, renewal, rotation, isolation)
- Sync contract reconciliation (canonical models, idempotency, partial rejection)
- Server-authoritative assessment grading & integer basis-point mastery
- Learner link integrity and prevention of phantom account creation
"""
from __future__ import annotations

import base64
import os
import sys
import tempfile
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "backend"))

TMP_DB = tempfile.mktemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TMP_DB}"
os.environ["PERSISTENCE_BACKEND"] = "sqlite"
os.environ["TRANSLATION_PROVIDER"] = "mock"
os.environ["LLM_PROVIDER"] = "mock"
os.environ["RETRIEVAL_PROVIDER"] = "local_hybrid"
os.environ["EMBEDDINGS_PROVIDER"] = "mock"

from app.core.settings import reset_settings_cache
from app.domain.ruleset import reset_ruleset_cache
from app.adapters.persistence import reset_persistence_for_tests
from app.adapters.ai.translation import reset_translation_cache
from app.adapters.ai.retrieval import reset_retrieval_cache
from app.adapters.ai.generation import reset_generation_cache
from app.content.pack_loader import reset_pack_cache, load_pack_index
from app.main import create_app

reset_settings_cache()
reset_ruleset_cache()
reset_translation_cache()
reset_retrieval_cache()
reset_generation_cache()
reset_pack_cache()


@pytest.fixture(scope="module")
def app_client():
    app = create_app()
    with TestClient(app) as c:
        yield c


def _gen_spki():
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    pk = ec.generate_private_key(ec.SECP256R1())
    spki = pk.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
    return pk, base64.urlsafe_b64encode(spki).decode().rstrip("=")


def test_auth_bearer_tokens_and_activation(app_client):
    """Test full auth lifecycle: device reg, learner create, activation with Bearer."""
    pk, spki_b64 = _gen_spki()
    # 1. Device registration
    r = app_client.post("/api/v1/devices", json={"public_key_spki_b64": spki_b64})
    assert r.status_code == 201
    dev_tokens = r.json()
    device_id = dev_tokens["device_id"]
    access_token = dev_tokens["access_token"]
    refresh_token = dev_tokens["refresh_token"]
    assert device_id.startswith("dev_")
    assert access_token and refresh_token

    # 2. Learner creation with Bearer token
    headers = {"Authorization": f"Bearer {access_token}"}
    r = app_client.post("/api/v1/learners", json={"display_label": "TestLearner1"}, headers=headers)
    assert r.status_code == 201
    learner_data = r.json()
    learner_id = learner_data["learner_id"]
    assert learner_id.startswith("lrn_")

    # 3. Activation WITHOUT token must fail with 401
    r = app_client.post(f"/api/v1/learners/{learner_id}/activate", headers={"X-Device-Id": device_id})
    assert r.status_code == 401
    assert "application/problem+json" in r.headers["content-type"]

    # 4. Activation WITH invalid token must fail with 401
    r = app_client.post(
        f"/api/v1/learners/{learner_id}/activate",
        headers={"Authorization": "Bearer invalid_junk_token", "X-Device-Id": device_id},
    )
    assert r.status_code == 401

    # 5. Activation WITH valid Bearer token succeeds
    r = app_client.post(
        f"/api/v1/learners/{learner_id}/activate",
        headers={"Authorization": f"Bearer {access_token}", "X-Device-Id": device_id},
    )
    assert r.status_code == 200
    active_auth = r.json()
    assert active_auth["learner_id"] == learner_id
    assert active_auth["device_token"]
    assert active_auth["refresh_token"]

    # 6. Refresh token rotation
    r = app_client.post("/api/v1/auth/refresh", json={"device_id": device_id, "refresh_token": refresh_token})
    assert r.status_code == 200
    rot = r.json()
    new_access = rot["access_token"]
    new_refresh = rot["refresh_token"]
    assert new_access != access_token
    assert new_refresh != refresh_token

    # 7. Reusing consumed refresh token fails with 401
    r = app_client.post("/api/v1/auth/refresh", json={"device_id": device_id, "refresh_token": refresh_token})
    assert r.status_code == 401


def test_device_and_learner_isolation(app_client):
    """Device B cannot activate or sync learner linked to Device A."""
    _pk1, spki1 = _gen_spki()
    _pk2, spki2 = _gen_spki()

    dev1 = app_client.post("/api/v1/devices", json={"public_key_spki_b64": spki1}).json()
    dev2 = app_client.post("/api/v1/devices", json={"public_key_spki_b64": spki2}).json()

    # Create learner on dev1
    h1 = {"Authorization": f"Bearer {dev1['access_token']}"}
    l1 = app_client.post("/api/v1/learners", json={"display_label": "Dev1Learner"}, headers=h1).json()

    # Dev2 tries to activate dev1's learner -> 403 Forbidden
    h2 = {"Authorization": f"Bearer {dev2['access_token']}"}
    r = app_client.post(f"/api/v1/learners/{l1['learner_id']}/activate", headers=h2)
    assert r.status_code == 403
    assert "not linked" in r.json()["detail"].lower()

    # Dev2 tries to sync for dev1's learner -> 403 Forbidden
    sync_req = {
        "device_id": dev2["device_id"],
        "learner_id": l1["learner_id"],
        "from_seq": 0,
        "events": [],
    }
    r = app_client.post("/api/v1/sync", json=sync_req, headers=h2)
    assert r.status_code == 403


def test_sync_contract_and_authoritative_grading(app_client):
    """Authoritative grading: client correctness claim is ignored, pack key is authoritative."""
    _pk, spki = _gen_spki()
    dev = app_client.post("/api/v1/devices", json={"public_key_spki_b64": spki}).json()
    h = {"Authorization": f"Bearer {dev['access_token']}"}
    l = app_client.post("/api/v1/learners", json={"display_label": "SyncLearner"}, headers=h).json()

    pack = load_pack_index()
    q = next(q for q in pack.questions.values() if q.concept_id == "c0001" and q.qtype == "mcq")

    # Client submits wrong answer (q.correct_option + 1) but claims correct_claim=True
    wrong_opt = (q.correct_option + 1) % len(q.options)
    ev_wrong = {
        "event_id": "evt_grade_test_wrong_1",
        "device_id": dev["device_id"],
        "learner_id": l["learner_id"],
        "seq": 1,
        "client_ts": int(time.time() * 1000),
        "type": "ANSWER_SUBMITTED",
        "concept_id": "c0001",
        "question_id": q.question_id,
        "payload": {
            "attempt_id": "att_w1",
            "question_id": q.question_id,
            "revision": 1,
            "response": wrong_opt,
            "correct_claim": True,  # Server must NOT trust this
        },
    }

    r = app_client.post(
        "/api/v1/sync",
        json={"device_id": dev["device_id"], "learner_id": l["learner_id"], "from_seq": 0, "events": [ev_wrong]},
        headers=h,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["results"][0]["outcome"] == "ACCEPTED"
    m = next(rec for rec in body["mastery"] if rec["concept_id"] == "c0001")
    # Wrong answer from initial 2000 bp drops mastery (to 1758 bp), NOT rises
    assert m["p_bp"] < 2000
    assert m["correct"] == 0
    assert m["attempts"] == 1

    # Client now submits correct answer with correct_option
    ev_correct = {
        "event_id": "evt_grade_test_correct_2",
        "device_id": dev["device_id"],
        "learner_id": l["learner_id"],
        "seq": 2,
        "client_ts": int(time.time() * 1000),
        "type": "ANSWER_SUBMITTED",
        "concept_id": "c0001",
        "question_id": q.question_id,
        "payload": {
            "attempt_id": "att_c2",
            "question_id": q.question_id,
            "revision": 1,
            "response": q.correct_option,
        },
    }
    r = app_client.post(
        "/api/v1/sync",
        json={"device_id": dev["device_id"], "learner_id": l["learner_id"], "from_seq": 1, "events": [ev_correct]},
        headers=h,
    )
    assert r.status_code == 200
    body2 = r.json()
    assert body2["results"][0]["outcome"] == "ACCEPTED"
    m2 = next(rec for rec in body2["mastery"] if rec["concept_id"] == "c0001")
    # Correct answer increases mastery
    assert m2["p_bp"] > m["p_bp"]
    assert m2["correct"] == 1
    assert m2["attempts"] == 2
    assert m2["last_event_seq"] == 2


def test_sync_legacy_fields_normalization_and_idempotency(app_client):
    """Test schema defense-in-depth: 'ts' -> 'client_ts', legacy event types, and idempotency."""
    _pk, spki = _gen_spki()
    dev = app_client.post("/api/v1/devices", json={"public_key_spki_b64": spki}).json()
    h = {"Authorization": f"Bearer {dev['access_token']}"}
    l = app_client.post("/api/v1/learners", json={"display_label": "LegacySyncLearner"}, headers=h).json()

    # Send legacy event format: 'ts' instead of 'client_ts', and 'lesson_opened'
    ev_legacy = {
        "event_id": "evt_legacy_format_1",
        "device_id": dev["device_id"],
        "learner_id": l["learner_id"],
        "seq": 1,
        "ts": int(time.time() * 1000),
        "event_type": "lesson_opened",
        "concept_id": "c0001",
        "payload": {"last_action": "VIEW"},
    }

    r = app_client.post(
        "/api/v1/sync",
        json={"device_id": dev["device_id"], "learner_id": l["learner_id"], "from_seq": 0, "events": [ev_legacy]},
        headers=h,
    )
    assert r.status_code == 200
    res = r.json()["results"]
    assert res[0]["outcome"] == "ACCEPTED"

    # Resubmitting identical event returns DUPLICATE
    r2 = app_client.post(
        "/api/v1/sync",
        json={"device_id": dev["device_id"], "learner_id": l["learner_id"], "from_seq": 0, "events": [ev_legacy]},
        headers=h,
    )
    assert r2.status_code == 200
    assert r2.json()["results"][0]["outcome"] == "DUPLICATE"


def test_sync_unknown_question_revision_does_not_mutate_mastery(app_client):
    """Submitting answer to unknown/legacy question version returns ACCEPTED with LEGACY_QUESTION, no mastery change."""
    _pk, spki = _gen_spki()
    dev = app_client.post("/api/v1/devices", json={"public_key_spki_b64": spki}).json()
    h = {"Authorization": f"Bearer {dev['access_token']}"}
    l = app_client.post("/api/v1/learners", json={"display_label": "RevLearner"}, headers=h).json()

    ev_rev = {
        "event_id": "evt_unknown_rev_1",
        "device_id": dev["device_id"],
        "learner_id": l["learner_id"],
        "seq": 1,
        "client_ts": int(time.time() * 1000),
        "type": "ANSWER_SUBMITTED",
        "concept_id": "c0001",
        "payload": {
            "attempt_id": "att_rev_99",
            "question_id": "q_unknown_999",
            "revision": 999,
            "response": 0,
        },
    }

    r = app_client.post(
        "/api/v1/sync",
        json={"device_id": dev["device_id"], "learner_id": l["learner_id"], "from_seq": 0, "events": [ev_rev]},
        headers=h,
    )
    assert r.status_code == 200
    res = r.json()["results"][0]
    assert res["outcome"] == "ACCEPTED"
    assert res["effect"] == "none"
    assert res["reason"] == "LEGACY_QUESTION"
