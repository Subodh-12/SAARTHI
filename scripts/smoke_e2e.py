"""End-to-end smoke test of the SAARTHI MVP loop (v2), using a temp SQLite DB.

Verifies:
- Auth: device registration (ECDSA P-256 public key) + learner creation +
  short-lived access / rotating refresh tokens + signed challenge renewal
- Assessment: MCQ submit → integer BKT mastery update (basis points) →
  event persisted
- Decision: deterministic v2 engine, needs_help flag, ruleset version
- Sync: idempotent replay, per-event outcome (v2 enum), integer mastery
- Doubt: orchestration graph runs translate→retrieve→generate→validate with
  the extractive fallback and produces a generation record
"""
from __future__ import annotations

import asyncio
import base64
import os
import sys
import tempfile
import time
from pathlib import Path

# Ensure the backend is importable
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "backend"))

# Use a temp DB for this smoke test
TMP_DB = tempfile.mktemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TMP_DB}"
os.environ["PERSISTENCE_BACKEND"] = "sqlite"
os.environ["TRANSLATION_PROVIDER"] = "mock"
os.environ["LLM_PROVIDER"] = "mock"
os.environ["RETRIEVAL_PROVIDER"] = "local_hybrid"
os.environ["EMBEDDINGS_PROVIDER"] = "mock"

# Reset caches
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

from app.adapters.persistence.repositories import (
    SqlDecisionRepository, SqlDeviceRepository, SqlEventRepository,
    SqlGenerationRecordRepository, SqlLearnerRepository, SqlMasteryRepository,
    SqlPackRepository,
)
from app.services import AuthService, AssessmentService, DecisionService, DoubtService, SyncService
from app.domain.schemas import (
    AssessmentSubmission, DoubtRequest, EventType, LearnerEvent,
    LearnerProfileCreate, NetworkState, new_device_id, new_event_id,
)
from app.content.pack_loader import load_pack_index


def _device_key():
    """Simulate the phone's non-extractable WebCrypto ECDSA P-256 key."""
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.serialization import (
        Encoding, PublicFormat,
    )
    private_key = ec.generate_private_key(ec.SECP256R1())
    spki = private_key.public_key().public_bytes(
        Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
    return private_key, base64.urlsafe_b64encode(spki).decode().rstrip("=")


async def main():
    p = await reset_persistence_for_tests()
    learners = SqlLearnerRepository(p)
    devices = SqlDeviceRepository(p)
    events = SqlEventRepository(p)
    mastery = SqlMasteryRepository(p)
    decisions = SqlDecisionRepository(p)
    gen_records = SqlGenerationRecordRepository(p)
    packs_repo = SqlPackRepository(p)

    pack = load_pack_index()
    auth = AuthService(learners, devices)
    assessment = AssessmentService(pack, events, mastery)
    decision_svc = DecisionService(pack, mastery, decisions)
    doubt = DoubtService(pack, decisions, gen_records)
    sync = SyncService(events, mastery, decisions, pack=pack, persistence=p)

    # 1. Device register (ECDSA P-256 public key) + learner create
    private_key, spki_b64 = _device_key()
    tokens = await auth.register_device(spki_b64, "shared-android-low-end")
    device_id = tokens.device_id
    auth_resp = await auth.create_learner(device_id, LearnerProfileCreate(display_label="Student1"))
    print(f"[1] learner={auth_resp.learner_id} device={auth_resp.device_id} "
          f"access_ttl_ok={tokens.access_expires_at > int(time.time()*1000)}")

    # 1b. Signed challenge/renewal (long-offline recovery path)
    nonce, _exp = await auth.new_challenge(device_id)
    from cryptography.hazmat.primitives import hashes
    der_sig = private_key.sign(nonce.encode("utf-8"),
                               __import__("cryptography.hazmat.primitives.asymmetric.ec", fromlist=["ECDSA"]).ECDSA(hashes.SHA256()))
    from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
    r, s = decode_dss_signature(der_sig)
    sig_b64 = base64.urlsafe_b64encode(r.to_bytes(32, "big") + s.to_bytes(32, "big")).decode().rstrip("=")
    renewed = await auth.renew_with_signature(device_id, nonce, sig_b64)
    print(f"[1b] signed challenge renewal ok={bool(renewed.access_token)}")

    # 2. Submit an MCQ (correct answer)
    q = next(q for q in pack.questions.values() if q.concept_id == "c0001" and q.qtype == "mcq")
    sub = AssessmentSubmission(
        question_id=q.question_id, selected_option=q.correct_option,
        duration_ms=4200, submitted_at=int(time.time() * 1000),
        attempt_id="att-smoke-1",
    )
    result = await assessment.submit_assessment(
        auth_resp.learner_id, device_id, sub, seq=1)
    print(f"[2] mcq correct: {result.correct} evidence={result.evidence.value} "
          f"bloom_level={result.bloom_level.value if result.bloom_level else None} "
          f"mastery.p_bp={result.mastery_after.p_bp} band={result.mastery_after.band}")
    assert result.correct, "MCQ correct should be True"
    assert result.mastery_after.p_bp == 6000, "first correct answer = 6000 bp (Appendix A)"
    assert result.bloom_level == q.bloom_level, "bloom_level should match question"
    assert result.bloom_mastery_after is not None, "bloom_mastery_after should be populated"
    assert result.bloom_mastery_after.p_bp == 6000, "first bloom mastery step = 6000 bp"

    # 3. Submit an MCQ (incorrect answer)
    wrong_option = (q.correct_option + 1) % len(q.options)
    sub2 = AssessmentSubmission(
        question_id=q.question_id, selected_option=wrong_option,
        duration_ms=5100, submitted_at=int(time.time() * 1000),
        attempt_id="att-smoke-2",
    )
    result2 = await assessment.submit_assessment(
        auth_resp.learner_id, device_id, sub2, seq=2)
    print(f"[3] mcq wrong: {result2.correct} mastery.p_bp={result2.mastery_after.p_bp}")
    assert not result2.correct, "MCQ wrong should be False"
    assert result2.mastery_after.p_bp < result.mastery_after.p_bp, "mastery should drop"

    # 4. Get next decision (v2 engine, trigger_correct drives WRONG_RETRY)
    decision = await decision_svc.next_decision(
        auth_resp.learner_id, NetworkState.ONLINE,
        trigger_event_type=EventType.ANSWER_SUBMITTED.value,
        trigger_concept_id="c0001",
        trigger_correct=False,
        recent_events=[],
    )
    print(f"[4] decision: action={decision.action.value} target={decision.target_concept_id} "
          f"delivery={decision.delivery_mode.value} reason={decision.reason_code} "
          f"needs_help={decision.needs_help} ruleset={decision.ruleset_version}")
    assert decision.action.value in ("REMEDIATE", "RETRY", "REVISE", "ADVANCE")
    assert decision.target_concept_id, "target_concept_id should be set"
    assert decision.target_bloom_level is not None, "target_bloom_level should be set"
    assert decision.reason_code in (
        "WEAK_CONCEPT", "WRONG_RETRY", "WEAK_PREREQ_GAP", "PARTIAL_PRACTICE")

    # 5. Sync — a fresh event at a NEW seq (the assessment already used 1-2),
    # then re-submit it for DUPLICATE (idempotent, no double effect).
    ev1 = LearnerEvent(
        event_id=new_event_id(), device_id=device_id, seq=10,
        learner_id=auth_resp.learner_id, client_ts=int(time.time() * 1000),
        event_type=EventType.CONTENT_VIEWED, concept_id="c0001",
        payload={"last_action": "VIEW"},
    )
    from app.domain.schemas import SyncRequest
    sync_resp = await sync.sync(SyncRequest(
        device_id=device_id, learner_id=auth_resp.learner_id,
        from_seq=0, events=[ev1],
    ))
    print(f"[5] sync: outcomes={[r.outcome.value for r in sync_resp.results]} "
          f"decision_status={sync_resp.decision_status}")
    assert sync_resp.results[0].outcome.value == "ACCEPTED"
    assert sync_resp.mastery, "canonical mastery should be returned"
    assert sync_resp.bloom_mastery is not None, "canonical bloom mastery should be returned"
    assert isinstance(sync_resp.mastery[0].p_bp, int)
    print(f"    mastery[0]: concept={sync_resp.mastery[0].concept_id} "
          f"p_bp={sync_resp.mastery[0].p_bp} band={sync_resp.mastery[0].band} "
          f"bloom_records={len(sync_resp.bloom_mastery)}")

    # 5b. Idempotent resubmission → DUPLICATE, no double effect.
    sync_resp2 = await sync.sync(SyncRequest(
        device_id=device_id, learner_id=auth_resp.learner_id,
        from_seq=0, events=[ev1],
    ))
    assert sync_resp2.results[0].outcome.value == "DUPLICATE"

    # 6. Doubt — ask an Odia question; extractive answer + generation record
    doubt_resp = await doubt.ask(DoubtRequest(
        query="ପଦାର୍ଥ ଶିଖ — କଠିନ ତରଳ ଗ୍ୟାସ କଣ?",
        learner_id=auth_resp.learner_id, pack_ids=["pack_class9_science_or_v1"],
    ))
    print(f"[6] doubt: provenance={doubt_resp.answer.provenance} "
          f"citations={doubt_resp.answer.citations} "
          f"retrieved_chunks={len(doubt_resp.retrieved.chunks)} "
          f"gen_record={doubt_resp.generation_record.record_id if doubt_resp.generation_record else None}")
    assert doubt_resp.answer.text_or, "answer should have text"
    assert doubt_resp.retrieved.chunks, "should retrieve chunks"
    assert doubt_resp.answer.provenance in ("extractive", "llm_grounded", "basic")
    assert doubt_resp.generation_record is not None
    assert doubt_resp.generation_record.prompt_version

    # 6b. Generation record persisted by the service layer (providers never
    # write to the DB).
    saved = await gen_records.list_for_decision(doubt_resp.decision_id)
    assert saved, "generation record should be persisted"

    await p.dispose()
    try:
        os.unlink(TMP_DB)
    except OSError:
        pass
    print("\n*** ALL SMOKE CHECKS PASSED ***")


if __name__ == "__main__":
    asyncio.run(main())
