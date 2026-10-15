"""v2 sync tests — transactional ingestion, per-event outcomes, replay.

Covers (v2 Section 8/9 + Section 5.4 of the repair brief):
  - four documented outcomes, exactly one per event
  - idempotent resubmission (DUPLICATE)
  - payload conflict on the same (device_id, seq) → REJECTED + tombstone,
    later events unaffected
  - repeated attempt_id → ACCEPTED with REPEAT_SUBMISSION, no mastery effect
  - unknown question revision → ACCEPTED with LEGACY_QUESTION
  - late arrival → projection rebuilt by canonical replay
  - partial acceptance: rejected event does not block later events
  - failed decision computation → decision_status=deferred, events kept
  - mastery is integer basis points and equals a canonical replay
"""
from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

import pytest
import pytest_asyncio

REPO = Path(__file__).resolve().parents[2]
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
from app.content.pack_loader import load_pack_index, reset_pack_cache
from app.domain.schemas import (
    EventType, LearnerEvent, LearnerProfile, Outcome, SyncEffect, SyncReason,
    SyncRequest, new_device_id, new_event_id, new_learner_id,
)
from app.services import SyncService
from app.domain.schemas import new_decision_id  # noqa: F401

reset_pack_cache()
_PACK = None


def _pack_correct_response(question_id: str):
    """The server regrades from its OWN answer key — tests must send the
    response that matches the pack's key to produce a correct answer."""
    global _PACK
    if _PACK is None:
        _PACK = load_pack_index()
    q = _PACK.get_question(question_id)
    return q.correct_option if (q and q.qtype == "mcq") else "answer"


@pytest_asyncio.fixture
async def setup():
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
        learner_id=learner_id, display_label="T", created_at=int(time.time() * 1000),
        locale="or", grade="class9", subject="science",
    )
    await learners.create_learner(profile, device_id)
    yield svc, learner_id, device_id, events, mastery, p
    await p.dispose()


def _answer_event(device_id, learner_id, seq, *, correct=True, attempt=None,
                  question_id=None, concept_id="c0001", revision=1,
                  event_id=None):
    qid = question_id or "q_ch01_c0001_01"
    key = _pack_correct_response(qid)
    response = key if correct else (1 if key != 1 else 0)
    return LearnerEvent(
        event_id=event_id or new_event_id(), device_id=device_id,
        learner_id=learner_id, seq=seq, client_ts=int(time.time() * 1000),
        event_type=EventType.ANSWER_SUBMITTED, concept_id=concept_id,
        question_id=qid,
        payload={
            "attempt_id": attempt or f"att-{seq}",
            "question_id": qid,
            "revision": revision,
            "response": response,
            "correct": correct,
            "last_action": "ASSESS",
        },
    )


def _view_event(device_id, learner_id, seq):
    return LearnerEvent(
        event_id=new_event_id(), device_id=device_id, learner_id=learner_id,
        seq=seq, client_ts=int(time.time() * 1000),
        event_type=EventType.CONTENT_VIEWED, concept_id="c0001",
        payload={"last_action": "VIEW"},
    )


async def test_one_outcome_per_event_and_accepted_mastery(setup):
    svc, lid, did, *_ = setup
    ev1 = _answer_event(did, lid, 1)
    ev2 = _view_event(did, lid, 2)
    resp = await svc.sync(SyncRequest(device_id=did, learner_id=lid,
                                      from_seq=0, events=[ev1, ev2]))
    assert len(resp.results) == 2
    by_seq = {r.seq: r for r in resp.results}
    assert by_seq[1].outcome == Outcome.ACCEPTED
    assert by_seq[1].effect == SyncEffect.MASTERY_UPDATED
    assert by_seq[2].outcome == Outcome.ACCEPTED
    assert by_seq[2].effect == SyncEffect.NONE
    # Mastery is integer basis points.
    m = [x for x in resp.mastery if x.concept_id == "c0001"]
    assert m and isinstance(m[0].p_bp, int) and 100 <= m[0].p_bp <= 9900
    assert m[0].p_bp == 6000  # first correct answer from p_init 2000


async def test_duplicate_resubmission(setup):
    svc, lid, did, *_ = setup
    ev = _answer_event(did, lid, 1)
    resp = await svc.sync(SyncRequest(device_id=did, learner_id=lid,
                                      from_seq=0, events=[ev]))
    assert resp.results[0].outcome == Outcome.ACCEPTED
    resp2 = await svc.sync(SyncRequest(device_id=did, learner_id=lid,
                                       from_seq=0, events=[ev]))
    assert resp2.results[0].outcome == Outcome.DUPLICATE
    # No double effect: mastery unchanged after the duplicate.
    m = [x for x in resp2.mastery if x.concept_id == "c0001"]
    assert m[0].attempts == 1


async def test_payload_conflict_rejected_tombstoned_later_events_ok(setup):
    """Same (device_id, seq) with a DIFFERENT event_id → permanent
    PAYLOAD_CONFLICT; the rejected event never blocks later events."""
    svc, lid, did, events, mastery, p = setup
    ev1 = _answer_event(did, lid, 1)
    await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0,
                               events=[ev1]))
    # A different event at the same seq:
    conflict = _answer_event(did, lid, 1, correct=False,
                             event_id=new_event_id())
    later = _answer_event(did, lid, 2, attempt="att-2")
    resp = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0,
                                      events=[conflict, later]))
    by_seq = {r.seq: r for r in resp.results}
    assert by_seq[1].outcome == Outcome.REJECTED
    assert by_seq[1].reason == SyncReason.PAYLOAD_CONFLICT
    # Later events proceed.
    assert by_seq[2].outcome == Outcome.ACCEPTED
    # Tombstone + diagnostics recorded; nothing silently deleted.
    from sqlalchemy import text
    async with p.engine.connect() as c:
        dead = (await c.execute(text(
            "SELECT reason FROM dead_letter_events WHERE seq = 1"))).fetchall()
    assert dead and dead[0][0] == "PAYLOAD_CONFLICT"


async def test_repeat_submission_accepted_without_effect(setup):
    svc, lid, did, *_ = setup
    ev1 = _answer_event(did, lid, 1, attempt="att-A")
    ev2 = _answer_event(did, lid, 2, attempt="att-A",
                        question_id="q_ch01_c0001_01")  # same attempt_id
    resp = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0,
                                      events=[ev1, ev2]))
    by_seq = {r.seq: r for r in resp.results}
    assert by_seq[1].outcome == Outcome.ACCEPTED
    assert by_seq[2].outcome == Outcome.ACCEPTED
    assert by_seq[2].reason == SyncReason.REPEAT_SUBMISSION
    assert by_seq[2].effect == SyncEffect.NONE
    m = [x for x in resp.mastery if x.concept_id == "c0001"]
    assert m[0].attempts == 1


async def test_unknown_question_revision_legacy(setup):
    svc, lid, did, *_ = setup
    ev = _answer_event(did, lid, 1, revision=99)
    resp = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0,
                                      events=[ev]))
    r = resp.results[0]
    assert r.outcome == Outcome.ACCEPTED
    assert r.effect == SyncEffect.NONE
    assert r.reason == SyncReason.LEGACY_QUESTION
    assert not resp.mastery  # no mastery rows created


async def test_mastery_equals_canonical_replay_after_late_arrival(setup):
    """A late event triggers a rebuild; the projection must equal a
    canonical replay of the accepted log (v2 replay invariant)."""
    svc, lid, did, events, mastery, p = setup
    # seq 1 and 2 first.
    ev1 = _answer_event(did, lid, 1, correct=True)
    ev2 = _answer_event(did, lid, 2, correct=True, attempt="att-2")
    await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0,
                               events=[ev1, ev2]))
    # Deliver seq 5 before seq 3/4 exist (out-of-order arrival across batches).
    ev5 = _answer_event(did, lid, 5, correct=True, attempt="att-5")
    resp1 = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=2,
                                       events=[ev5]))
    assert resp1.results[0].outcome == Outcome.ACCEPTED
    # Now deliver seq 3 (below the last applied 5) → full rebuild path.
    ev3 = _answer_event(did, lid, 3, correct=True, attempt="att-3")
    ev4 = _answer_event(did, lid, 4, correct=True, attempt="att-4")
    resp2 = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=2,
                                       events=[ev3, ev4]))
    assert all(r.outcome == Outcome.ACCEPTED for r in resp2.results)
    # Canonical replay oracle: 5 correct answers in seq order from p_init.
    from app.domain.bkt import bkt_update_bp
    from app.domain.ruleset import get_ruleset
    ruleset = get_ruleset()
    expected = 2000
    for _ in range(5):
        expected = bkt_update_bp(expected, True, ruleset)
    m = [x for x in resp2.mastery if x.concept_id == "c0001"]
    assert m[0].p_bp == expected
    assert m[0].attempts == 5


async def test_decision_failure_does_not_rollback_events(setup, monkeypatch):
    """A failed post-commit decision → decision_status=deferred; accepted
    events and mastery remain committed."""
    svc, lid, did, events, mastery, p = setup
    ev = _answer_event(did, lid, 1)
    async def boom(*a, **kw):
        raise RuntimeError("decision engine exploded")
    monkeypatch.setattr(svc, "_post_sync_decision", boom)
    resp = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0,
                                      events=[ev]))
    assert resp.decision_status == "deferred"
    assert resp.decision is None
    # Events were accepted and mastery committed.
    assert resp.results[0].outcome == Outcome.ACCEPTED
    m = [x for x in resp.mastery if x.concept_id == "c0001"]
    assert m and m[0].attempts == 1


async def test_batch_transaction_all_or_nothing(setup, monkeypatch):
    """A failing batch transaction → every event RETRYABLE and nothing
    partially applied (v2 Section 8)."""
    svc, lid, did, events, mastery, p = setup
    ev1 = _answer_event(did, lid, 1)
    ev2 = _answer_event(did, lid, 2, attempt="att-2")
    # Sabotage the projection step inside the transaction.
    original = svc._session_apply
    async def broken(*a, **kw):
        raise RuntimeError("db gone mid-batch")
    monkeypatch.setattr(svc, "_session_apply", broken)
    resp = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0,
                                      events=[ev1, ev2]))
    assert all(r.outcome == Outcome.RETRYABLE for r in resp.results)
    assert len(resp.results) == 2
    # Nothing applied: no mastery rows, no events persisted.
    assert await mastery.get_mastery(lid) == []
    from sqlalchemy import text
    async with p.engine.connect() as c:
        n = (await c.execute(text(
            "SELECT COUNT(*) FROM learner_events"))).scalar()
    assert n == 0


async def test_out_of_order_batch_rejected(setup):
    svc, lid, did, *_ = setup
    from app.core.errors import SaarthiError
    ev1 = _answer_event(did, lid, 5)
    ev2 = _answer_event(did, lid, 3)
    with pytest.raises(SaarthiError):
        await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0,
                                   events=[ev1, ev2]))


async def test_learner_mismatch_rejected_and_tombstoned(setup):
    svc, lid, did, events, mastery, p = setup
    ev = _answer_event(did, lid, 1)
    ev.learner_id = new_learner_id()
    resp = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0,
                                      events=[ev]))
    r = resp.results[0]
    assert r.outcome == Outcome.REJECTED
    assert r.reason == SyncReason.LEARNER_NOT_LINKED
    from sqlalchemy import text
    async with p.engine.connect() as c:
        n = (await c.execute(text(
            "SELECT COUNT(*) FROM dead_letter_events"))).scalar()
    assert n == 1


async def test_rejected_event_does_not_block_later_events(setup):
    """INVALID_PAYLOAD (no concept, no question) is rejected; later events
    in the same batch proceed (v2: rejected never blocks later events)."""
    svc, lid, did, *_ = setup
    bad = LearnerEvent(
        event_id=new_event_id(), device_id=did, learner_id=lid, seq=1,
        client_ts=int(time.time() * 1000), event_type=EventType.ANSWER_SUBMITTED,
        concept_id=None, payload={"attempt_id": "att-bad", "correct": True},
    )
    good = _answer_event(did, lid, 2)
    resp = await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0,
                                      events=[bad, good]))
    by_seq = {r.seq: r for r in resp.results}
    assert by_seq[1].outcome == Outcome.REJECTED
    assert by_seq[1].reason == SyncReason.INVALID_PAYLOAD
    assert by_seq[2].outcome == Outcome.ACCEPTED
    assert by_seq[2].effect == SyncEffect.MASTERY_UPDATED


async def test_sync_cursor_advances_only_on_processed(setup):
    svc, lid, did, events, mastery, p = setup
    ev1 = _answer_event(did, lid, 1)
    await svc.sync(SyncRequest(device_id=did, learner_id=lid, from_seq=0,
                               events=[ev1]))
    acked, _srv = await events.get_sync_cursor(did, lid)
    assert acked == 1
