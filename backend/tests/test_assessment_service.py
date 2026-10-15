"""Assessment flow tests (v2 — integer basis-point mastery, server regrade)."""
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
from app.domain.assess import evaluate_submission, evaluate_short_answer
from app.domain.bkt import bkt_update_bp, mastery_band_bp
from app.domain.schemas import (
    AssessmentSubmission, EvidenceType, EventType, LearnerProfile,
    new_device_id,
)
from app.services import AssessmentService
from app.domain.ruleset import get_ruleset


@pytest_asyncio.fixture
async def setup_db():
    p = await reset_persistence_for_tests()
    events = SqlEventRepository(p)
    mastery = SqlMasteryRepository(p)
    pack = load_pack_index()
    svc = AssessmentService(pack, events, mastery)
    learner_id = "lrn_0123456789abcdef"
    device_id = new_device_id()
    profile = LearnerProfile(
        learner_id=learner_id, display_label="Test", created_at=int(time.time() * 1000),
        locale="or", grade="class9", subject="science",
    )
    await SqlLearnerRepository(p).create_learner(profile, device_id)
    yield svc, learner_id, device_id, pack
    await p.dispose()


async def test_mcq_correct_updates_mastery_in_bp(setup_db):
    svc, learner_id, device_id, pack = setup_db
    q = next(q for q in pack.questions.values() if q.qtype == "mcq" and q.concept_id == "c0001")
    sub = AssessmentSubmission(
        question_id=q.question_id, selected_option=q.correct_option,
        duration_ms=4200, submitted_at=int(time.time() * 1000),
        attempt_id="att-correct-1",
    )
    result = await svc.submit_assessment(learner_id, device_id, sub, seq=1)
    assert result.correct is True
    assert result.evidence == EvidenceType.CORRECT
    # Mastery in integer basis points, risen above p_init (2000).
    assert isinstance(result.mastery_after.p_bp, int)
    assert result.mastery_after.p_bp > 2000
    assert result.mastery_after.p_bp == 6000  # exact Appendix A first step


async def test_mcq_incorrect_drops_mastery(setup_db):
    svc, learner_id, device_id, pack = setup_db
    q = next(q for q in pack.questions.values() if q.qtype == "mcq" and q.concept_id == "c0001")
    wrong_option = (q.correct_option + 1) % len(q.options)
    sub = AssessmentSubmission(
        question_id=q.question_id, selected_option=wrong_option,
        duration_ms=5100, submitted_at=int(time.time() * 1000),
        attempt_id="att-wrong-1",
    )
    result = await svc.submit_assessment(learner_id, device_id, sub, seq=1)
    assert result.correct is False
    assert result.evidence == EvidenceType.INCORRECT
    assert result.mastery_after.p_bp < 2000
    assert result.mastery_after.p_bp >= 100  # clamped


async def test_short_answer_partial(setup_db):
    svc, learner_id, device_id, pack = setup_db
    q = next(q for q in pack.questions.values() if q.qtype == "short_answer" and q.concept_id == "c0002")
    sub = AssessmentSubmission(
        question_id=q.question_id, answer_text="ଘନତ୍ୱ ହେଉଛି ମାତ୍ରା ଓ ଆୟତନର ଅନୁପାତ",
        duration_ms=3000, submitted_at=int(time.time() * 1000),
        attempt_id="att-sa-1",
    )
    result = await svc.submit_assessment(learner_id, device_id, sub, seq=1)
    assert result.evidence in (EvidenceType.PARTIAL, EvidenceType.INCORRECT)


async def test_event_persistence_after_submit(setup_db):
    svc, learner_id, device_id, pack = setup_db
    q = next(q for q in pack.questions.values() if q.qtype == "mcq")
    sub = AssessmentSubmission(
        question_id=q.question_id, selected_option=q.correct_option,
        duration_ms=4200, submitted_at=int(time.time() * 1000),
        attempt_id="att-persist-1",
    )
    await svc.submit_assessment(learner_id, device_id, sub, seq=5)
    evs = await svc.events.list_events(learner_id, since_seq=0)
    assert any(e.seq == 5 for e in evs)
    # v2 event type recorded.
    assert any(e.event_type == EventType.ANSWER_SUBMITTED for e in evs)


def test_bkt_update_correct_rises():
    ruleset = get_ruleset()
    p_new = bkt_update_bp(4000, True, ruleset, "c0001")
    assert p_new > 4000
    p_new2 = bkt_update_bp(p_new, True, ruleset, "c0001")
    assert p_new2 > p_new  # near-mastery keeps climbing


def test_bkt_update_incorrect_drops():
    ruleset = get_ruleset()
    p_new = bkt_update_bp(8000, False, ruleset, "c0001")
    assert p_new < 8000


def test_bkt_update_never_leaves_clamp_band():
    ruleset = get_ruleset()
    p = 2000
    for _ in range(10):
        p = bkt_update_bp(p, True, ruleset)
    assert p <= 9900
    p = 9000
    for _ in range(10):
        p = bkt_update_bp(p, False, ruleset)
    assert p >= 100


def test_mastery_band_boundaries():
    ruleset = get_ruleset()
    assert mastery_band_bp(3999, ruleset) == "weak"
    assert mastery_band_bp(4000, ruleset) == "partial"
    assert mastery_band_bp(8499, ruleset) == "partial"
    assert mastery_band_bp(8500, ruleset) == "mastered"


def test_only_graded_answers_map_to_mastery():
    """Non-assessment events never carry mastery evidence (v2 Section 6)."""
    from app.domain.bkt import mastery_effect_for_event
    from app.domain.schemas import LearnerEvent, new_event_id
    ruleset = get_ruleset()
    view = LearnerEvent(event_id=new_event_id(), device_id=new_device_id(),
                        learner_id="lrn_0123456789abcdef", seq=1,
                        client_ts=0, event_type=EventType.CONTENT_VIEWED,
                        payload={})
    effect = mastery_effect_for_event(view, ruleset, set())
    assert effect.effect == "none"
