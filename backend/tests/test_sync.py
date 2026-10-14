"""Sync contract tests (v2) — batch limits, canonical ordering.

The deep per-event outcome coverage lives in test_sync_v2.py; this module
keeps the request-level contract checks that existed in the v1 suite,
migrated to the v2 API.
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
from app.content.pack_loader import load_pack_index
from app.core.errors import SaarthiError
from app.domain.schemas import (
    EventType, LearnerEvent, LearnerProfile, Outcome, SyncRequest,
    new_device_id, new_event_id, new_learner_id,
)
from app.services import SyncService


@pytest_asyncio.fixture
async def setup():
    p = await reset_persistence_for_tests()
    events = SqlEventRepository(p)
    mastery = SqlMasteryRepository(p)
    decisions = SqlDecisionRepository(p)
    learners = SqlLearnerRepository(p)
    svc = SyncService(events, mastery, decisions, pack=load_pack_index(),
                      persistence=p)
    learner_id = new_learner_id()
    device_id = new_device_id()
    profile = LearnerProfile(
        learner_id=learner_id, display_label="T", created_at=int(time.time() * 1000),
        locale="or", grade="class9", subject="science",
    )
    await learners.create_learner(profile, device_id)
    yield svc, learner_id, device_id, events
    await p.dispose()


def _view_event(device_id, learner_id, seq):
    return LearnerEvent(
        event_id=new_event_id(), device_id=device_id, learner_id=learner_id,
        seq=seq, client_ts=int(time.time() * 1000),
        event_type=EventType.CONTENT_VIEWED, concept_id="c0001",
        payload={"last_action": "VIEW"},
    )


async def test_sync_batch_too_large(setup):
    svc, learner_id, device_id, _ = setup
    big_batch = [_view_event(device_id, learner_id, i + 1) for i in range(200)]
    with pytest.raises(SaarthiError):
        await svc.sync(SyncRequest(device_id=device_id, learner_id=learner_id,
                                   from_seq=0, events=big_batch))


async def test_sync_out_of_order_rejected(setup):
    svc, learner_id, device_id, _ = setup
    ev1 = _view_event(device_id, learner_id, 5)
    ev2 = _view_event(device_id, learner_id, 3)
    with pytest.raises(SaarthiError) as e:
        await svc.sync(SyncRequest(device_id=device_id, learner_id=learner_id,
                                   from_seq=0, events=[ev1, ev2]))
    assert "ordering" in str(e.value).lower() or "ordering" in e.value.detail.lower()


async def test_sync_outcomes_use_v2_enum_values(setup):
    """Outcomes are the frozen v2 enum: ACCEPTED/DUPLICATE/RETRYABLE/REJECTED."""
    svc, learner_id, device_id, _ = setup
    ev = _view_event(device_id, learner_id, 1)
    resp = await svc.sync(SyncRequest(device_id=device_id, learner_id=learner_id,
                                      from_seq=0, events=[ev]))
    assert resp.results[0].outcome == Outcome.ACCEPTED
    resp2 = await svc.sync(SyncRequest(device_id=device_id, learner_id=learner_id,
                                       from_seq=0, events=[ev]))
    assert resp2.results[0].outcome == Outcome.DUPLICATE


async def test_sync_returns_next_decision(setup):
    """Sync computes a post-commit decision with status 'computed'."""
    svc, learner_id, device_id, _ = setup
    ev = _view_event(device_id, learner_id, 1)
    resp = await svc.sync(SyncRequest(device_id=device_id, learner_id=learner_id,
                                      from_seq=0, events=[ev]))
    assert resp.decision_status == "computed"
    assert resp.decision is not None
    assert resp.decision.target_concept_id
    # Local decisions for the same state stay preserved as source=local on
    # the phone; the server decision arrives as source=server (v2 Section 9).
    assert resp.decision.source == "server"


async def test_sync_empty_batch_returns_mastery(setup):
    svc, learner_id, device_id, _ = setup
    resp = await svc.sync(SyncRequest(device_id=device_id, learner_id=learner_id,
                                      from_seq=0, events=[]))
    assert resp.results == []
    assert resp.mastery == []
    assert resp.ruleset_version
