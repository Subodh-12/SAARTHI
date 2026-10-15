"""Comprehensive end-to-end tests for Bloom's Taxonomy in SAARTHI.

Covers:
  - Canonical Bloom domain model, ordering, transitions, and localized Odia labels
  - Question schema validation and pack integrity (100% valid Bloom levels)
  - Assessment service integer-BKT updates per Bloom level
  - SqlMasteryRepository persistence of learner_bloom_progress
  - Sync service projection, replay consistency, and SyncResponse payload
  - Shared-device profile isolation (no leakage of Bloom mastery across profiles)
  - Adaptive decision engine target Bloom level selection and fallback
"""
from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

import pytest
import pytest_asyncio
from pydantic import ValidationError

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
from app.domain.bloom import (
    BLOOM_ORDER, BLOOM_LABELS_EN, BLOOM_LABELS_OR, BLOOM_DESCRIPTIONS_OR,
    BloomLevel, bloom_complexity, bloom_description, bloom_label,
    compare_bloom, is_valid_bloom_level, next_higher_level, next_lower_level,
    parse_bloom_level,
)
from app.domain.decide import (
    DecisionInput, MasteryEntry, decide, select_target_bloom_level,
)
from app.domain.ruleset import get_ruleset
from app.domain.schemas import (
    Action, AssessmentSubmission, BloomMasteryRecord, EventType,
    LearnerEvent, LearnerProfile, Question, SyncRequest,
    new_device_id, new_event_id, new_learner_id,
)
from app.services import AssessmentService, DecisionService, SyncService


# --------------------------------------------------------------------------- #
# 1. Canonical Bloom domain contract & localized labels
# --------------------------------------------------------------------------- #
def test_bloom_domain_contract():
    assert len(BLOOM_ORDER) == 6
    assert [b.value for b in BLOOM_ORDER] == [
        "remember", "understand", "apply", "analyze", "evaluate", "create",
    ]

    # Complexity ranking and comparison
    for i, b in enumerate(BLOOM_ORDER):
        assert bloom_complexity(b) == i

    assert compare_bloom(BloomLevel.REMEMBER, BloomLevel.UNDERSTAND) == -1
    assert compare_bloom(BloomLevel.APPLY, BloomLevel.APPLY) == 0
    assert compare_bloom(BloomLevel.CREATE, BloomLevel.EVALUATE) == 1

    # Transitions
    assert next_higher_level(BloomLevel.REMEMBER) == BloomLevel.UNDERSTAND
    assert next_higher_level(BloomLevel.EVALUATE) == BloomLevel.CREATE
    assert next_higher_level(BloomLevel.CREATE) is None

    assert next_lower_level(BloomLevel.CREATE) == BloomLevel.EVALUATE
    assert next_lower_level(BloomLevel.UNDERSTAND) == BloomLevel.REMEMBER
    assert next_lower_level(BloomLevel.REMEMBER) is None

    # Parsing & validation
    assert parse_bloom_level("  REMEMBER  ") == BloomLevel.REMEMBER
    assert parse_bloom_level("apply") == BloomLevel.APPLY
    assert parse_bloom_level(BloomLevel.ANALYZE) == BloomLevel.ANALYZE
    assert is_valid_bloom_level("evaluate") is True
    assert is_valid_bloom_level("unknown_level") is False

    with pytest.raises(ValueError, match="Invalid Bloom taxonomy level"):
        parse_bloom_level("invalid_level")

    # Localized labels (Odia-first)
    assert bloom_label(BloomLevel.REMEMBER, "or") == "ମନେରଖିବା"
    assert bloom_label(BloomLevel.UNDERSTAND, "or") == "ବୁଝିବା"
    assert bloom_label(BloomLevel.APPLY, "or") == "ପ୍ରୟୋଗ"
    assert bloom_label(BloomLevel.ANALYZE, "or") == "ବିଶ୍ଳେଷଣ"
    assert bloom_label(BloomLevel.EVALUATE, "or") == "ମୂଲ୍ୟାଙ୍କନ"
    assert bloom_label(BloomLevel.CREATE, "or") == "ନିର୍ମାଣ"

    assert bloom_label(BloomLevel.REMEMBER, "en") == "Remember"
    assert bloom_description(BloomLevel.REMEMBER, "or") == BLOOM_DESCRIPTIONS_OR[BloomLevel.REMEMBER]
    assert len(bloom_description(BloomLevel.APPLY, "or")) > 5


# --------------------------------------------------------------------------- #
# 2. Schema validation & Question model
# --------------------------------------------------------------------------- #
def test_question_schema_requires_valid_bloom():
    # Valid Question with BloomLevel enum or string
    q = Question(
        question_id="q_test_bloom_01",
        concept_id="c0001",
        chapter_id="ch001",
        qtype="mcq",
        prompt_or="ପରୀକ୍ଷା ପ୍ରଶ୍ନ",
        options=["A", "B", "C", "D"],
        correct_option=0,
        bloom_level=BloomLevel.APPLY,
        explanation_or="ବ୍ୟାଖ୍ୟା",
        difficulty="medium",
        source_ref="NCERT_9_SC_CH1",
    )
    assert q.bloom_level == BloomLevel.APPLY

    # String input gets parsed/validated as BloomLevel
    q2 = Question(
        question_id="q_test_bloom_02",
        concept_id="c0001",
        chapter_id="ch001",
        qtype="mcq",
        prompt_or="ପରୀକ୍ଷା ପ୍ରଶ୍ନ",
        options=["A", "B"],
        correct_option=1,
        bloom_level="analyze",  # type: ignore
        explanation_or="ବ୍ୟାଖ୍ୟା",
        difficulty="hard",
        source_ref="NCERT_9_SC_CH1",
    )
    assert q2.bloom_level == BloomLevel.ANALYZE

    # Invalid bloom level is rejected
    with pytest.raises(ValidationError):
        Question(
            question_id="q_test_bloom_bad",
            concept_id="c0001",
            chapter_id="ch001",
            qtype="mcq",
            prompt_or="ପରୀକ୍ଷା ପ୍ରଶ୍ନ",
            options=["A", "B"],
            correct_option=0,
            bloom_level="genius_level",  # type: ignore
            explanation_or="ବ୍ୟାଖ୍ୟା",
            difficulty="easy",
            source_ref="NCERT_9_SC_CH1",
        )


# --------------------------------------------------------------------------- #
# 3. Pack questions Bloom taxonomy integrity
# --------------------------------------------------------------------------- #
def test_pack_questions_bloom_integrity():
    reset_pack_cache()
    pack = load_pack_index()
    assert len(pack.questions) > 0

    for qid, q in pack.questions.items():
        assert isinstance(q.bloom_level, BloomLevel), f"Question {qid} must have a valid BloomLevel"
        assert q.bloom_level in BLOOM_ORDER

    # PackLoader available_bloom_levels_for_concept
    for cid in pack.concepts:
        levels = pack.available_bloom_levels_for_concept(cid)
        assert len(levels) > 0
        for lvl in levels:
            assert is_valid_bloom_level(lvl)


# --------------------------------------------------------------------------- #
# Fixture for DB & services
# --------------------------------------------------------------------------- #
@pytest_asyncio.fixture
async def setup_db():
    p = await reset_persistence_for_tests()
    events = SqlEventRepository(p)
    mastery = SqlMasteryRepository(p)
    decisions = SqlDecisionRepository(p)
    pack = load_pack_index()
    assessment_svc = AssessmentService(pack, events, mastery)
    sync_svc = SyncService(events, mastery, decisions, pack, p)

    learner_id = "lrn_bloomtest00000001"
    device_id = new_device_id()
    profile = LearnerProfile(
        learner_id=learner_id, display_label="Bloom Tester", created_at=int(time.time() * 1000),
        locale="or", grade="class9", subject="science",
    )
    await SqlLearnerRepository(p).create_learner(profile, device_id)
    yield assessment_svc, sync_svc, mastery, learner_id, device_id, pack
    await p.dispose()


# --------------------------------------------------------------------------- #
# 4. Assessment Service updates Bloom mastery via BKT
# --------------------------------------------------------------------------- #
@pytest.mark.asyncio
async def test_assessment_service_updates_bloom_mastery(setup_db):
    assessment_svc, _, mastery_repo, learner_id, device_id, pack = setup_db

    # Pick a question with concept c0001
    q = next(q for q in pack.questions.values() if q.qtype == "mcq" and q.concept_id == "c0001")
    q_bloom = q.bloom_level

    # Submit correct answer
    sub = AssessmentSubmission(
        question_id=q.question_id,
        selected_option=q.correct_option,
        duration_ms=3500,
        submitted_at=int(time.time() * 1000),
        attempt_id="att_bloom_test_01",
        correct_claim=True,
    )
    res = await assessment_svc.submit_assessment(learner_id, device_id, sub, seq=1)

    assert res.correct is True
    assert res.bloom_level == q_bloom
    assert res.bloom_mastery_after is not None
    assert res.bloom_mastery_after.concept_id == q.concept_id
    assert res.bloom_mastery_after.bloom_level == q_bloom
    # BKT: initial 2000 -> 6000 bp on correct
    assert res.bloom_mastery_after.p_bp == 6000
    assert res.bloom_mastery_after.band == "partial"
    assert res.bloom_mastery_after.attempts == 1
    assert res.bloom_mastery_after.correct == 1

    # Verify persisted in learner_bloom_progress
    stored_bloom = await mastery_repo.get_bloom_mastery(learner_id, q.concept_id)
    bm_row = next((r for r in stored_bloom if r.bloom_level == q_bloom), None)
    assert bm_row is not None
    assert bm_row.p_bp == 6000
    assert bm_row.attempts == 1
    assert bm_row.correct == 1


# --------------------------------------------------------------------------- #
# 5. Sync Service Bloom projection and replay consistency
# --------------------------------------------------------------------------- #
@pytest.mark.asyncio
async def test_sync_projection_and_replay_bloom(setup_db):
    _, sync_svc, mastery_repo, learner_id, device_id, pack = setup_db

    q1 = next(q for q in pack.questions.values() if q.qtype == "mcq" and q.concept_id == "c0001")
    q1_bloom = q1.bloom_level

    now = int(time.time() * 1000)
    ev1 = LearnerEvent(
        event_id=new_event_id(),
        device_id=device_id,
        learner_id=learner_id,
        seq=1,
        type=EventType.ANSWER_SUBMITTED,
        client_ts=now,
        concept_id=q1.concept_id,
        chapter_id=q1.chapter_id,
        question_id=q1.question_id,
        payload={
            "question_id": q1.question_id,
            "revision": 1,
            "attempt_id": "att_sync_bloom_01",
            "response": q1.correct_option,
            "correct_claim": True,
            "duration_ms": 3000,
            "submitted_at": now,
            "bloom_level": q1_bloom.value,
        },
    )

    req = SyncRequest(
        device_id=device_id,
        learner_id=learner_id,
        from_seq=0,
        events=[ev1],
    )
    resp = await sync_svc.sync(req)

    assert len(resp.results) == 1
    assert resp.results[0].outcome.value == "ACCEPTED"
    assert len(resp.bloom_mastery) >= 1

    # Verify bloom mastery in response
    bm = next((b for b in resp.bloom_mastery if b.concept_id == q1.concept_id and b.bloom_level == q1_bloom), None)
    assert bm is not None
    assert bm.p_bp == 6000
    assert bm.attempts == 1
    assert bm.correct == 1

    # Verify canonical_bloom_mastery list format
    cbm = next((b for b in resp.canonical_bloom_mastery if b.concept_id == q1.concept_id and b.bloom_level == q1_bloom), None)
    assert cbm is not None
    assert cbm.p_bp == 6000

    # Test replay idempotency: replaying existing sequence does not corrupt state
    req2 = SyncRequest(
        device_id=device_id,
        learner_id=learner_id,
        from_seq=0,
        events=[ev1],
    )
    resp2 = await sync_svc.sync(req2)
    assert len(resp2.results) == 1
    assert resp2.results[0].outcome.value == "DUPLICATE"
    bm2 = next((b for b in resp2.bloom_mastery if b.concept_id == q1.concept_id and b.bloom_level == q1_bloom), None)
    assert bm2 is not None
    assert bm2.p_bp == 6000


# --------------------------------------------------------------------------- #
# 6. Profile Isolation: Bloom mastery is strictly per-profile
# --------------------------------------------------------------------------- #
@pytest.mark.asyncio
async def test_profile_isolation_bloom(setup_db):
    assessment_svc, _, mastery_repo, learner_a, device_id, pack = setup_db

    # Create learner B on the same device
    learner_b = "lrn_bloomtest00000002"
    profile_b = LearnerProfile(
        learner_id=learner_b, display_label="Learner B", created_at=int(time.time() * 1000),
        locale="or", grade="class9", subject="science",
    )
    persistence = mastery_repo.p
    await SqlLearnerRepository(persistence).create_learner(profile_b, device_id)

    q = next(q for q in pack.questions.values() if q.qtype == "mcq" and q.concept_id == "c0001")
    # Learner A answers correctly
    sub = AssessmentSubmission(
        question_id=q.question_id,
        selected_option=q.correct_option,
        duration_ms=4000,
        submitted_at=int(time.time() * 1000),
        attempt_id="att_iso_01",
        correct_claim=True,
    )
    await assessment_svc.submit_assessment(learner_a, device_id, sub, seq=1)

    # Learner A has Bloom mastery
    bm_a_list = await mastery_repo.get_bloom_mastery(learner_a, q.concept_id)
    assert any(r.bloom_level == q.bloom_level and r.p_bp == 6000 for r in bm_a_list)

    # Learner B has NO Bloom mastery on this concept (strict profile isolation)
    bm_b_list = await mastery_repo.get_bloom_mastery(learner_b, q.concept_id)
    assert len(bm_b_list) == 0

    b_all = await mastery_repo.get_bloom_mastery(learner_b)
    assert len(b_all) == 0


# --------------------------------------------------------------------------- #
# 7. Adaptive Decision Engine Target Bloom Selection & Fallback
# --------------------------------------------------------------------------- #
def test_adaptive_target_bloom_level_selection():
    ruleset = get_ruleset()
    available_all = ["remember", "understand", "apply", "analyze", "evaluate", "create"]

    # Cold start / weak (< 4000 bp): foundational target (remember)
    inp_weak = DecisionInput(
        trigger_event_type="SESSION_STARTED",
        trigger_concept_id=None,
        trigger_correct=None,
        mastery={"c0001": MasteryEntry(p_bp=2000)},
        recent_events=[],
        prereqs={"c0001": []},
        concept_order=["c0001"],
        available_bloom_levels_for_concept={"c0001": available_all},
    )
    out_weak = decide(inp_weak, ruleset)
    assert out_weak.target_bloom_level == "remember"

    # Partial mastery: once remember is proficient (>= 7000 bp), target advances to understand
    inp_partial = DecisionInput(
        trigger_event_type="ANSWER_SUBMITTED",
        trigger_concept_id="c0001",
        trigger_correct=True,
        mastery={"c0001": MasteryEntry(p_bp=5000)},
        recent_events=[],
        prereqs={"c0001": []},
        concept_order=["c0001"],
        bloom_mastery={"c0001": {"remember": MasteryEntry(p_bp=7500)}},
        available_bloom_levels_for_concept={"c0001": available_all},
    )
    target_partial = select_target_bloom_level(
        action="RETRY",
        target_concept_id="c0001",
        reason_code="PARTIAL_PRACTICE",
        inp=inp_partial,
        ruleset=ruleset,
    )
    assert target_partial == "understand"

    # Proficient mastery: once remember & understand are proficient (>= 7000 bp), target advances to apply
    inp_proficient = DecisionInput(
        trigger_event_type="ANSWER_SUBMITTED",
        trigger_concept_id="c0001",
        trigger_correct=True,
        mastery={"c0001": MasteryEntry(p_bp=7500)},
        recent_events=[],
        prereqs={"c0001": []},
        concept_order=["c0001"],
        bloom_mastery={"c0001": {
            "remember": MasteryEntry(p_bp=7500),
            "understand": MasteryEntry(p_bp=7200),
        }},
        available_bloom_levels_for_concept={"c0001": available_all},
    )
    target_proficient = select_target_bloom_level(
        action="RETRY",
        target_concept_id="c0001",
        reason_code="PARTIAL_PRACTICE",
        inp=inp_proficient,
        ruleset=ruleset,
    )
    assert target_proficient == "apply"

    # RETRY with remember, understand, and apply proficient (>= 7000 bp): advances to analyze
    inp_higher = DecisionInput(
        trigger_event_type="ANSWER_SUBMITTED",
        trigger_concept_id="c0001",
        trigger_correct=True,
        mastery={"c0001": MasteryEntry(p_bp=8000)},
        recent_events=[],
        prereqs={"c0001": []},
        concept_order=["c0001"],
        bloom_mastery={"c0001": {
            "remember": MasteryEntry(p_bp=7500),
            "understand": MasteryEntry(p_bp=7200),
            "apply": MasteryEntry(p_bp=7100),
        }},
        available_bloom_levels_for_concept={"c0001": available_all},
    )
    target_higher = select_target_bloom_level(
        action="RETRY",
        target_concept_id="c0001",
        reason_code="PARTIAL_PRACTICE",
        inp=inp_higher,
        ruleset=ruleset,
    )
    assert target_higher == "analyze"

    # REVISE on SLICE_COMPLETE targets the highest available Bloom level for synthesis
    target_slice = select_target_bloom_level(
        action="REVISE",
        target_concept_id="c0001",
        reason_code="SLICE_COMPLETE",
        inp=inp_higher,
        ruleset=ruleset,
    )
    assert target_slice == "create"

    # ADVANCE to a new concept starts at the foundational level (remember)
    target_advance = select_target_bloom_level(
        action="ADVANCE",
        target_concept_id="c0001",
        reason_code="MASTERED_ADVANCE",
        inp=inp_higher,
        ruleset=ruleset,
    )
    assert target_advance == "remember"

    # Safe Fallback: if higher order levels are not available in pack, safely falls back
    inp_limited = DecisionInput(
        trigger_event_type="ANSWER_SUBMITTED",
        trigger_concept_id="c0001",
        trigger_correct=True,
        mastery={"c0001": MasteryEntry(p_bp=8000)},
        recent_events=[],
        prereqs={"c0001": []},
        concept_order=["c0001"],
        bloom_mastery={"c0001": {
            "remember": MasteryEntry(p_bp=7500),
            "understand": MasteryEntry(p_bp=7200),
            "apply": MasteryEntry(p_bp=7100),
        }},
        available_bloom_levels_for_concept={"c0001": ["remember", "understand"]},
    )
    target_fallback = select_target_bloom_level(
        action="RETRY",
        target_concept_id="c0001",
        reason_code="PARTIAL_PRACTICE",
        inp=inp_limited,
        ruleset=ruleset,
    )
    assert target_fallback == "understand"
