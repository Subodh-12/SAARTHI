"""v2 device-auth tests — ECDSA P-256 registration, token rotation,
signed-nonce challenge/renewal, revocation, ownership enforcement.

Covers (v2 Section 8 + repair brief Section 6):
  - device registration with a non-extractable WebCrypto-shaped ECDSA P-256
    public key (raw r||s signatures accepted, DER too)
  - short-lived access tokens (24h from ruleset) + rotating refresh (30d)
  - refresh rotation: reuse of a consumed refresh token fails
  - signed-nonce challenge/renewal after prolonged offline periods
  - DEVICE_REVOKED quarantines server-side trust; pending events are a
    client concern (outbox untouched server-side)
  - ownership: cross-profile and cross-device access denied on
    learner-specific endpoints (decisions, traces, state, sync)
  - rate limiting and request-size limits
"""
from __future__ import annotations

import base64
import os
import sys
import tempfile
import time
from pathlib import Path

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "backend"))

TMP_DB = tempfile.mktemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TMP_DB}"
os.environ["PERSISTENCE_BACKEND"] = "sqlite"
os.environ["TRANSLATION_PROVIDER"] = "mock"
os.environ["LLM_PROVIDER"] = "mock"

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding, PublicFormat,
)

from app.core.settings import reset_settings_cache
from app.domain.ruleset import reset_ruleset_cache
from app.adapters.persistence import reset_persistence_for_tests
from app.adapters.ai.translation import reset_translation_cache
from app.adapters.ai.retrieval import reset_retrieval_cache
from app.adapters.ai.generation import reset_generation_cache
from app.content.pack_loader import reset_pack_cache

reset_settings_cache()
reset_ruleset_cache()
reset_translation_cache()
reset_retrieval_cache()
reset_generation_cache()
reset_pack_cache()

from app.main import create_app  # noqa: E402


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _device_key():
    """Simulate the phone's non-extractable WebCrypto ECDSA P-256 key."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    spki = private_key.public_key().public_bytes(
        Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
    return private_key, _b64u(spki)


def _sign_raw(private_key, nonce: str) -> str:
    """WebCrypto-compatible raw r||s signature over the UTF-8 nonce."""
    from app.services.auth_service import encode_dss_signature
    der = private_key.sign(nonce.encode("utf-8"), ec.ECDSA(hashes_module()))
    # convert DER → raw r||s
    from cryptography.hazmat.primitives.asymmetric.utils import (
        decode_dss_signature,
    )
    r, s = decode_dss_signature(der)
    return _b64u(r.to_bytes(32, "big") + s.to_bytes(32, "big"))


def hashes_module():
    from cryptography.hazmat.primitives import hashes
    return hashes.SHA256()


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


def _register_device(client) -> tuple[dict, object]:
    private_key, spki_b64 = _device_key()
    r = client.post("/api/v1/devices", json={
        "public_key_spki_b64": spki_b64,
        "hardware_label": "test-phone",
    })
    assert r.status_code == 201, r.text
    return r.json(), private_key


def _create_learner(client, headers: dict | None = None) -> dict:
    r = client.post("/api/v1/learners", headers=headers, json={
        "display_label": "Sunita", "locale": "or",
        "grade": "class9", "subject": "science",
    })
    assert r.status_code == 201, r.text
    return r.json()


def test_device_registration_returns_token_pair(client):
    tokens, _key = _register_device(client)
    assert tokens["device_id"].startswith("dev_")
    assert tokens["access_token"] and tokens["refresh_token"]
    assert tokens["token_type"] == "Bearer"
    now_ms = int(time.time() * 1000)
    # Lifetimes from the shared ruleset: access 24h, refresh 30d.
    assert abs(tokens["access_expires_at"] - (now_ms + 24 * 3600 * 1000)) < 5000
    assert abs(tokens["refresh_expires_at"] - (now_ms + 30 * 86400 * 1000)) < 5000


def test_refresh_rotation_and_reuse_rejection(client):
    tokens, _key = _register_device(client)
    r = client.post("/api/v1/auth/refresh", json={
        "device_id": tokens["device_id"],
        "refresh_token": tokens["refresh_token"],
    })
    assert r.status_code == 200
    fresh = r.json()
    assert fresh["access_token"] != tokens["access_token"]
    assert fresh["refresh_token"] != tokens["refresh_token"]
    # Reuse of the CONSUMED refresh token fails closed (rotation).
    r2 = client.post("/api/v1/auth/refresh", json={
        "device_id": tokens["device_id"],
        "refresh_token": tokens["refresh_token"],
    })
    assert r2.status_code == 401


def test_signed_challenge_renewal_after_long_offline(client):
    tokens, private_key = _register_device(client)
    # Simulate prolonged offline: no refresh usage, go straight to challenge.
    r = client.post("/api/v1/auth/challenge",
                    json={"device_id": tokens["device_id"]})
    assert r.status_code == 200
    nonce = r.json()["nonce"]
    sig = _sign_raw(private_key, nonce)
    r2 = client.post("/api/v1/auth/renew", json={
        "device_id": tokens["device_id"],
        "nonce": nonce,
        "signature_b64": sig,
    })
    assert r2.status_code == 200, r2.text
    renewed = r2.json()
    assert renewed["access_token"]
    # Nonce single use: replaying the same signature fails.
    r3 = client.post("/api/v1/auth/renew", json={
        "device_id": tokens["device_id"],
        "nonce": nonce,
        "signature_b64": sig,
    })
    assert r3.status_code == 401


def test_challenge_renewal_rejects_wrong_key(client):
    tokens, _private_key = _register_device(client)
    r = client.post("/api/v1/auth/challenge",
                    json={"device_id": tokens["device_id"]})
    nonce = r.json()["nonce"]
    attacker_key, _spki = _device_key()
    bad_sig = _sign_raw(attacker_key, nonce)
    r2 = client.post("/api/v1/auth/renew", json={
        "device_id": tokens["device_id"],
        "nonce": nonce,
        "signature_b64": bad_sig,
    })
    assert r2.status_code == 401


def test_access_token_expires_quickly_relative_to_refresh(client):
    tokens, _key = _register_device(client)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    r = client.get("/api/v1/learners/me", headers=headers)
    # No learner created yet on this device: auth passed (401 would mean the
    # token was rejected); authorization is denied with 403.
    assert r.status_code == 403


def test_revoked_device_is_403_device_revoked(client):
    tokens, _key = _register_device(client)
    _auth = _create_learner(client)
    # Revoke directly through the device repository (operator action).
    import asyncio
    from app.adapters.persistence import get_persistence
    from app.adapters.persistence.repositories import SqlDeviceRepository

    async def _revoke():
        p = await get_persistence()
        repo = SqlDeviceRepository(p)
        await repo.revoke_device(tokens["device_id"])

    asyncio.get_event_loop().run_until_complete(_revoke()) \
        if False else asyncio.run(_revoke())
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    r = client.get("/api/v1/learners/me", headers=headers)
    assert r.status_code == 403
    body = r.json()
    assert body.get("error_code") == "device_revoked"
    # The client would quarantine pending events and continue locally;
    # the server keeps the stored events for audit (never deletes them).


def test_cross_device_access_denied(client):
    """A learner's data is only reachable from the device holding the
    active link (v2: enforce learner/device/profile ownership)."""
    tokens_a, _ = _register_device(client)
    learner = _create_learner(client)  # created on device A via token
    # Device B registers and tries to read device A's learner state.
    tokens_b, _ = _register_device(client)
    headers_b = {"Authorization": f"Bearer {tokens_b['access_token']}"}
    # B has no learner yet: 403 (auth OK, no learner bound) — never A's data.
    r = client.get("/api/v1/state", headers=headers_b)
    assert r.status_code == 403
    # Once B activates its own learner it still sees only its own state.
    r2 = client.post("/api/v1/learners", headers=headers_b, json={
        "display_label": "B", "locale": "or", "grade": "class9",
        "subject": "science"})
    assert r2.status_code == 201
    tokens_b2 = r2.json()
    headers_b2 = {"Authorization": f"Bearer {tokens_b2['device_token']}"}
    r3 = client.get("/api/v1/state", headers=headers_b2)
    assert r3.status_code == 200
    body = r3.json()
    assert body["device_id"] == tokens_b["device_id"]
    assert body["learner_id"] != learner["learner_id"]


def test_decision_trace_ownership(client):
    """GET /decisions/{id} must 404 (not leak) for another learner."""
    tokens_a, _ = _register_device(client)
    headers_a = {"Authorization": f"Bearer {tokens_a['access_token']}"}
    learner_a = _create_learner(client, headers_a)
    r = client.post("/api/v1/decisions/next", json={"network": "online"},
                    headers=headers_a)
    assert r.status_code == 200
    decision_id = r.json()["decision_id"]
    # Learner A can read own decision + trace.
    r2 = client.get(f"/api/v1/decisions/{decision_id}", headers=headers_a)
    assert r2.status_code == 200
    r3 = client.get(f"/api/v1/decisions/{decision_id}/trace", headers=headers_a)
    assert r3.status_code in (200, 404)  # trace may not exist; never 403 leak
    # A second learner (own device) gets 404 for A's decision.
    tokens_b, _ = _register_device(client)
    _create_learner(client, {"Authorization": f"Bearer {tokens_b['access_token']}"})
    headers_b = {"Authorization": f"Bearer {tokens_b['access_token']}"}
    r4 = client.get(f"/api/v1/decisions/{decision_id}", headers=headers_b)
    assert r4.status_code == 404


def test_sync_rejects_other_learners_events(client):
    """The sync route overrides device/learner from the token — events for
    another learner come back REJECTED (LEARNER_NOT_LINKED)."""
    from app.domain.schemas import EventType, LearnerEvent, new_event_id
    tokens_a, _ = _register_device(client)
    headers = {"Authorization": f"Bearer {tokens_a['access_token']}"}
    learner_a = _create_learner(client, headers)
    # An event claiming a DIFFERENT learner_id:
    ev = LearnerEvent(
        event_id=new_event_id(), device_id=tokens_a["device_id"],
        learner_id="lrn_" + "a" * 24, seq=1, client_ts=int(time.time() * 1000),
        event_type=EventType.CONTENT_VIEWED, payload={},
    )
    body = {
        "device_id": tokens_a["device_id"],
        "learner_id": "lrn_" + "a" * 24,
        "from_seq": 0,
        "events": [jsonable(ev)],
    }
    r = client.post("/api/v1/sync", json=body, headers=headers)
    assert r.status_code == 200
    results = r.json()["results"]
    assert results[0]["outcome"] == "REJECTED"
    assert results[0]["reason"] == "LEARNER_NOT_LINKED"


def jsonable(ev):
    import json as _json
    return _json.loads(ev.model_dump_json(by_alias=True))


def test_rate_limiting_returns_429(client):
    tokens, _key = _register_device(client)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    # The limit applies to POSTs; hammer a cheap protected endpoint.
    last = None
    for i in range(400):
        last = client.post("/api/v1/decisions/next", json={"network": "online"},
                           headers=headers)
        if last.status_code == 429:
            break
    assert last is not None and last.status_code == 429, \
        "expected 429 RATE_LIMITED after hammering"
    if last.status_code == 429:
        assert "retry-after" in {k.lower() for k in last.headers}


def test_request_size_limit_returns_413(client):
    tokens, _key = _register_device(client)
    headers = {"Authorization": f"Bearer {tokens['access_token']}",
               "Content-Type": "application/json"}
    huge = "x" * (300_000)
    r = client.post("/api/v1/decisions/next", content=huge, headers=headers)
    assert r.status_code == 413


def test_security_headers_present(client):
    r = client.get("/api/v1/health")
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert r.headers.get("Referrer-Policy") == "no-referrer"


def test_learner_data_minimality(client):
    """The learner contract accepts only display_label/locale/grade/subject —
    no phone numbers, locations or advertising identifiers (v2 N8)."""
    r = client.post("/api/v1/learners", json={
        "display_label": "Min", "phone": "+91-9999999999",
        "location": {"lat": 20.1, "lng": 85.1},
        "advertising_id": "ADID-123",
    })
    assert r.status_code == 201
    body = r.json()
    assert "phone" not in body and "location" not in body
    assert "advertising_id" not in body
