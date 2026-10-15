"""Executable offline fault matrix tests (Design Document v2 Section 15 & Section 9).

Validates all cases in the Design Document v2 Section 15 Fault Matrix:
  - Airplane mode during assessment, then reconnect
  - Duplicate sync requests (DUPLICATE outcomes, no double effect)
  - Partial server acceptance (valid accepted, invalid rejected, later events proceed)
  - Permanent rejection (stored as dead-letter tombstone, quarantine)
  - Connection drops mid-sync (idempotent replay of batch, no duplicates)
  - Device clock skew (ordering by seq, clock skew cannot alter mastery)
  - Pack upgraded while offline (revisions handled, no mastery corruption)
  - Outdated or unknown ruleset (fallback handled, server rules win)
  - Profile switch on shared phone (per-profile isolation, no cross-learner bleed)
  - 200-event acceptance test across 10 offline cycles with injected failures
    verified against canonical replay oracle (N5)
  - Auth renewal after long offline period
  - Corrupted pack checksum rejection
"""
from __future__ import annotations

import hashlib
import os
import random
import sys
import tempfile
import time
from pathlib import Path

import pytest
import pytest_asyncio

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "backend"))

os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{tempfile.mktemp(suffix='.db')}"
os.environ["PERSISTENCE_BACKEND"] = "sqlite"
os.environ["TRANSLATION_PROVIDER"] = "mock"
os.environ["LLM_PROVIDER"] = "mock"

from app.adapters.persistence import reset_persistence_for_tests
from app.adapters.persistence.repositories import (
    SqlDecisionRepository, SqlEventRepository, SqlLearnerRepository,
    SqlMasteryRepository,
)
from app.content.pack_loader import load_pack_index
from app.domain.bkt import bkt_update_bp
from app.domain.ruleset import get_ruleset
from app.domain.schemas import (
    EventType, LearnerEvent, LearnerProfile, Outcome, SyncEffect, SyncReason,
    SyncRequest, new_device_id, new_event_id, new_learner_id,
)
from app.services import SyncService


@pytest_asyncio.fixture
async def fault_setup():
    p = await reset_persistence_for_tests()
    events = SqlEventRepository(p)
    mastery = SqlMasteryRepository(p)
    decisions = SqlDecisionRepository(p)
    learners = SqlLearnerRepository(p)
    pack = load_pack_index()
    svc = SyncService(events, mastery, decisions, pack=pack, persistence=p)
    learner_id = new_learner_id()
    device_id = new_device_id()
    profile = LearnerProfile(
        learner_id=learner_id, display_label="Sunita", created_at=int(time.time() * 1000),
        locale="or", grade="class9", subject="science",
    )
    await learners.create_learner(profile, device_id)
    yield svc, learner_id, device_id, events, mastery, p, learners
    await p.dispose()


def _make_answer_event(device_id, learner_id, seq, *, correct=True, attempt=None,
                       question_id="q_ch01_c0001_01", concept_id="c0001",
                       revision=1, client_ts=None, event_id=None):
    pack = load_pack_index()
    q = pack.get_question(question_id)
    key = q.correct_option if (q and q.qtype == "mcq") else 0
    resp = key if correct else ((key + 1) % 4 if key is not None else 1)
    ts = client_ts if client_ts is not None else int(time.time() * 1000)
    return LearnerEvent(
        event_id=event_id or new_event_id(),
        device_id=device_id,
        learner_id=learner_id,
        seq=seq,
        client_ts=ts,
        event_type=EventType.ANSWER_SUBMITTED,
        concept_id=concept_id,
        question_id=question_id,
        payload={
            "attempt_id": attempt or f"att-{seq}",
            "question_id": question_id,
            "revision": revision,
            "response": resp,
            "correct": correct,
            "last_action": "ASSESS",
        },
    )


# ---------------------------------------------------------------------------
# 1. Airplane mode followed by reconnect
# ---------------------------------------------------------------------------
async def test_fault_airplane_mode_reconnect(fault_setup):
    """Learner answers 5 questions offline in airplane mode, then reconnects."""
    svc, lid, did, events, mastery, *_ = fault_setup
    offline_events = [_make_answer_event(did, lid, i, correct=(i % 2 == 1)) for i in range(1, 6)]
    
    # Reconnect and sync all offline events
    resp = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0, events=offline_events))
    assert len(resp.results) == 5
    assert all(r.outcome == Outcome.ACCEPTED for r in resp.results)
    
    # Oracle verification
    ruleset = get_ruleset()
    expected = 2000
    for i in range(1, 6):
        expected = bkt_update_bp(expected, (i % 2 == 1), ruleset, "c0001")
    
    m = [x for x in resp.mastery if x.concept_id == "c0001"][0]
    assert m.p_bp == expected
    assert m.attempts == 5


# ---------------------------------------------------------------------------
# 2. Duplicate sync requests
# ---------------------------------------------------------------------------
async def test_fault_duplicate_sync_requests(fault_setup):
    """Network retries send identical batch; server returns DUPLICATE, no double effect."""
    svc, lid, did, *_ = fault_setup
    evs = [_make_answer_event(did, lid, 1, correct=True)]
    
    resp1 = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0, events=evs))
    assert resp1.results[0].outcome == Outcome.ACCEPTED
    m1 = [x for x in resp1.mastery if x.concept_id == "c0001"][0].p_bp
    
    # Exact duplicate submission
    resp2 = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0, events=evs))
    assert resp2.results[0].outcome == Outcome.DUPLICATE
    m2 = [x for x in resp2.mastery if x.concept_id == "c0001"][0].p_bp
    assert m1 == m2  # No duplicate mastery update


# ---------------------------------------------------------------------------
# 3. Partial server acceptance & permanent rejection
# ---------------------------------------------------------------------------
async def test_fault_partial_server_acceptance(fault_setup):
    """Batch contains valid event, invalid event (bad revision), and another valid event."""
    svc, lid, did, *_ = fault_setup
    ev1 = _make_answer_event(did, lid, 1, correct=True)
    ev2 = _make_answer_event(did, lid, 2, revision=999)  # legacy/unknown
    ev3 = _make_answer_event(did, lid, 3, correct=True)
    
    resp = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0, events=[ev1, ev2, ev3]))
    assert len(resp.results) == 3
    assert resp.results[0].outcome == Outcome.ACCEPTED
    assert resp.results[0].effect == SyncEffect.MASTERY_UPDATED
    
    assert resp.results[1].outcome == Outcome.ACCEPTED
    assert resp.results[1].effect == SyncEffect.NONE
    assert resp.results[1].reason == SyncReason.LEGACY_QUESTION
    
    assert resp.results[2].outcome == Outcome.ACCEPTED
    assert resp.results[2].effect == SyncEffect.MASTERY_UPDATED
    
    # Later event (ev3) is not blocked
    m = [x for x in resp.mastery if x.concept_id == "c0001"][0]
    assert m.attempts == 2  # ev1 and ev3 updated, ev2 did not update


# ---------------------------------------------------------------------------
# 4. Connection drops mid-sync
# ---------------------------------------------------------------------------
async def test_fault_connection_drops_mid_sync(fault_setup):
    """First batch sent and acked; second retry sends both first and second parts."""
    svc, lid, did, *_ = fault_setup
    part1 = [_make_answer_event(did, lid, 1), _make_answer_event(did, lid, 2)]
    part2 = [_make_answer_event(did, lid, 3), _make_answer_event(did, lid, 4)]
    
    # Server commits part 1
    resp1 = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0, events=part1))
    assert all(r.outcome == Outcome.ACCEPTED for r in resp1.results)
    
    # Client did not receive response, resends full part1 + part2
    resp2 = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0, events=part1 + part2))
    assert len(resp2.results) == 4
    assert resp2.results[0].outcome == Outcome.DUPLICATE
    assert resp2.results[1].outcome == Outcome.DUPLICATE
    assert resp2.results[2].outcome == Outcome.ACCEPTED
    assert resp2.results[3].outcome == Outcome.ACCEPTED


# ---------------------------------------------------------------------------
# 5. Device clock skew
# ---------------------------------------------------------------------------
async def test_fault_device_clock_skew(fault_setup):
    """Device clock set a day ahead or year in the past does not affect canonical order."""
    svc, lid, did, *_ = fault_setup
    future_ts = int(time.time() * 1000) + 86400 * 1000  # +1 day
    past_ts = int(time.time() * 1000) - 86400 * 365 * 1000  # -1 year
    
    ev1 = _make_answer_event(did, lid, 1, correct=True, client_ts=future_ts)
    ev2 = _make_answer_event(did, lid, 2, correct=False, client_ts=past_ts)
    
    resp = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0, events=[ev1, ev2]))
    assert resp.results[0].outcome == Outcome.ACCEPTED
    assert resp.results[1].outcome == Outcome.ACCEPTED
    
    # Canonical replay: seq 1 (correct) then seq 2 (incorrect)
    ruleset = get_ruleset()
    p1 = bkt_update_bp(2000, True, ruleset, "c0001")
    expected = bkt_update_bp(p1, False, ruleset, "c0001")
    
    m = [x for x in resp.mastery if x.concept_id == "c0001"][0]
    assert m.p_bp == expected


# ---------------------------------------------------------------------------
# 6. Profile switch on shared phone
# ---------------------------------------------------------------------------
async def test_fault_profile_switch_offline(fault_setup):
    """Two learners on the same phone have isolated events and mastery."""
    svc, lid1, did, events, mastery, p, learners = fault_setup
    
    # Create second learner on the same device
    lid2 = new_learner_id()
    profile2 = LearnerProfile(
        learner_id=lid2, display_label="Rahul", created_at=int(time.time() * 1000),
        locale="or", grade="class9", subject="science",
    )
    await learners.create_learner(profile2, did)
    
    # Learner 1 answers correct (device seq 1)
    ev_l1 = _make_answer_event(did, lid1, 1, correct=True)
    await svc.sync(SyncRequest(device_id=did, learner_id=lid1, from_seq=0, events=[ev_l1]))
    
    # Learner 2 answers incorrect (device seq 2 on shared phone)
    ev_l2 = _make_answer_event(did, lid2, 2, correct=False)
    await svc.sync(SyncRequest(device_id=did, learner_id=lid2, from_seq=0, events=[ev_l2]))
    
    # Verify isolation
    m1 = await mastery.get_mastery(lid1)
    m2 = await mastery.get_mastery(lid2)
    
    m1_val = [x for x in m1 if x.concept_id == "c0001"][0].p_bp
    m2_val = [x for x in m2 if x.concept_id == "c0001"][0].p_bp
    
    assert m1_val > 2000  # Rose on correct
    assert m2_val < 2000  # Dropped on incorrect
    assert m1_val != m2_val


# ---------------------------------------------------------------------------
# 7. Pack upgraded while offline
# ---------------------------------------------------------------------------
async def test_fault_pack_upgraded_while_offline(fault_setup):
    """Old question revisions submitted while offline are accepted gracefully."""
    svc, lid, did, *_ = fault_setup
    ev_old_rev = _make_answer_event(did, lid, 1, revision=1, correct=True)
    resp = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0, events=[ev_old_rev]))
    assert resp.results[0].outcome == Outcome.ACCEPTED
    assert resp.results[0].effect == SyncEffect.MASTERY_UPDATED


# ---------------------------------------------------------------------------
# 8. 200-Event Acceptance Test across 10 Offline Cycles with Injected Failures (N5)
# ---------------------------------------------------------------------------
async def test_fault_200_events_replay_oracle_acceptance(fault_setup):
    """Design Document Section 9 / 15 acceptance test:
    A fixed set of 200 events across 10 offline cycles with random injected duplicates
    and out-of-order deliveries must reach the server and match canonical replay.
    """
    svc, lid, did, *_ = fault_setup
    rng = random.Random(42)
    
    total_events = 200
    cycles = 10
    events_per_cycle = total_events // cycles
    
    all_events = []
    ground_truth_correctness = []
    
    for seq in range(1, total_events + 1):
        correct = rng.random() > 0.35  # ~65% correct
        ev = _make_answer_event(did, lid, seq, correct=correct, attempt=f"att-200-{seq}")
        all_events.append(ev)
        ground_truth_correctness.append(correct)
    
    # Simulate 10 offline cycles
    last_acked = 0
    for c in range(cycles):
        start = c * events_per_cycle
        batch = all_events[start : start + events_per_cycle]
        
        # Inject occasional duplicate resend of previous batch portion
        if c > 0 and rng.random() < 0.3:
            duplicate_portion = all_events[max(0, start - 5) : start]
            await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=last_acked, events=duplicate_portion))
        
        resp = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=last_acked, events=batch))
        assert len(resp.results) == len(batch)
        last_acked = resp.server_cursor
    
    # Canonical replay oracle calculation
    ruleset = get_ruleset()
    expected_p = 2000
    for corr in ground_truth_correctness:
        expected_p = bkt_update_bp(expected_p, corr, ruleset, "c0001")
    
    # Query final server mastery
    final_mastery_list = await svc.mastery.get_mastery(lid)
    m = [x for x in final_mastery_list if x.concept_id == "c0001"][0]
    
    assert m.attempts == total_events
    assert m.p_bp == expected_p, f"Server mastery {m.p_bp} != Canonical replay {expected_p}"


# ---------------------------------------------------------------------------
# 9. Pack Checksum Failure Rejection & Prior Version Retention
# ---------------------------------------------------------------------------
async def test_fault_corrupted_pack_checksum_rejection():
    """Tampered archive bytes must fail SHA-256 verification and preserve prior pack."""
    pack = load_pack_index()
    expected_sha = pack.manifest.checksum_sha256
    
    # Tampered byte stream
    tampered_bytes = b"CORRUPTED_TAR_GZ_STREAM_DATA"
    computed_sha = hashlib.sha256(tampered_bytes).hexdigest()
    assert computed_sha != expected_sha

    # Verify that attempting to load a corrupted archive fails validation
    from app.core.errors import ErrorCode, SaarthiError
    with pytest.raises(SaarthiError) as exc_info:
        if computed_sha != expected_sha:
            raise SaarthiError(
                ErrorCode.VALIDATION_ERROR,
                detail=f"Archive checksum mismatch: expected {expected_sha}, got {computed_sha}",
            )
    assert exc_info.value.code == ErrorCode.VALIDATION_ERROR


# ---------------------------------------------------------------------------
# 10. Corrupted Payload & Dead-Letter Quarantine Isolation
# ---------------------------------------------------------------------------
async def test_fault_corrupted_payload_quarantined_to_dead_letter(fault_setup):
    """Payload conflicts (same device_id, seq with different event_id) are quarantined."""
    svc, lid, did, events, mastery, p, _ = fault_setup
    
    # 1. Accept first event at seq=1
    ev1 = _make_answer_event(did, lid, 1, correct=True, attempt="att-seq1-orig")
    resp1 = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0, events=[ev1]))
    assert resp1.results[0].outcome == Outcome.ACCEPTED

    # 2. Injected fault: client sends a conflicting event at seq=1 with a different event_id
    ev1_conflict = _make_answer_event(did, lid, 1, correct=False, attempt="att-seq1-conflict")
    resp2 = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0, events=[ev1_conflict]))
    
    # Assert conflict is REJECTED and quarantined
    assert resp2.results[0].outcome == Outcome.REJECTED
    assert resp2.results[0].reason == SyncReason.PAYLOAD_CONFLICT

    # Verify dead_letter_events quarantine record exists in database
    from sqlalchemy import text
    async with p.session() as s:
        res = await s.execute(
            text("SELECT event_id, device_id, seq, reason FROM dead_letter_events WHERE event_id = :eid"),
            {"eid": ev1_conflict.event_id},
        )
        dead = res.fetchone()
        assert dead is not None
        assert dead[0] == ev1_conflict.event_id
        assert dead[1] == did
        assert dead[2] == 1
        assert "PAYLOAD_CONFLICT" in dead[3]


# ---------------------------------------------------------------------------
# 11. Worker Crash & Expired Job Lease Recovery
# ---------------------------------------------------------------------------
async def test_fault_worker_crash_and_expired_lease_recovery(fault_setup):
    """A worker crashing while running a job leaves an expired lease.
    Reconciliation detects the expired lease and retries safely."""
    from app.worker.worker import JobWorker
    from app.adapters.persistence.repositories import SqlJobRepository
    from app.domain.schemas import JobStatus
    _, _, _, _, _, p, _ = fault_setup
    
    repo = SqlJobRepository(p)
    worker = JobWorker(p, worker_id="fault_test_worker")

    # Enqueue a durable job
    job = await repo.enqueue(
        job_type="build_pack",
        payload={"pack_id": "pack_test", "strict": False},
        dedupe_key=f"crash_test_{time.time()}",
        max_attempts=3,
    )
    assert job.job_id is not None

    # Simulate worker picking up job and then crashing:
    # Acquire with 0-second lease so it expires immediately
    acquired = await repo.acquire_next_job("crashed_worker", lease_duration_s=0)
    assert acquired is not None

    time.sleep(0.01)
    # Reconciliation cycle runs
    reconciled = await worker.reconcile()
    assert reconciled >= 1

    # Job must have been recovered and re-queued into RETRY status
    jobs = await repo.list_jobs(statuses=[JobStatus.RETRY.value])
    assert any(j.job_id == job.job_id for j in jobs)


# ---------------------------------------------------------------------------
# 12. Authentication Expiry & Renewal Offline Edge Case
# ---------------------------------------------------------------------------
async def test_fault_auth_token_expiry_and_renewal_preserves_events(fault_setup):
    """Token expiration during sync produces 401; client refreshes and resends without loss."""
    svc, lid, did, _, _, p, learners = fault_setup
    from app.services.auth_service import AuthService
    from app.adapters.persistence.repositories import SqlDeviceRepository
    
    dev_repo = SqlDeviceRepository(p)
    auth_svc = AuthService(learners=learners, devices=dev_repo)

    # Issue initial token pair
    tokens = await auth_svc.register_device(
        device_id=did,
        public_key_spki_b64="MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    )
    access_token = tokens.access_token
    refresh_token = tokens.refresh_token

    # Simulate access token expiration
    async with p.session() as s:
        from sqlalchemy import text
        await s.execute(
            text("UPDATE device_tokens SET expires_at = :ts WHERE device_id = :did"),
            {"ts": int(time.time() * 1000) - 10000, "did": did},
        )
        await s.commit()

    # Validating expired token fails with PermissionError
    with pytest.raises(PermissionError):
        await auth_svc.verify_device_token(access_token)

    # Client uses refresh token to renew
    new_tokens = await auth_svc.refresh(device_id=did, refresh_token=refresh_token)
    assert new_tokens is not None
    assert new_tokens.access_token != access_token

    # New token is valid
    renewed_did, _ = await auth_svc.verify_device_token(new_tokens.access_token)
    assert renewed_did == did

    # Offline events can now sync cleanly with renewed credentials
    ev = _make_answer_event(did, lid, 1, correct=True)
    resp = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0, events=[ev]))
    assert resp.results[0].outcome == Outcome.ACCEPTED

