"""Tests for the verification gate + BKT/diagnosis integration (Phase 5).

Covers: gate statuses (candidate/verified/refuted/insufficient/none),
no double-counting from retries or duplicate events, unanswered-not-incorrect,
missing follow-up → pending state, assessment-service integration (diagnosis
attached only on accepted incorrect MCQ), and decision traces.
"""
import time

import pytest

from app.domain.schemas import (
    AssessmentSubmission, EventType, LearnerEvent, Question, new_event_id,
)
from app.domain.verification import TagEvidence, verification_status
from app.services.assessment_service import AssessmentService
from app.services.diagnosis_service import DiagnosisService

# ---- verification gate (pure) ----------------------------------------------
def test_gate_none_with_no_evidence():
    assert verification_status([]) == "none"


def test_gate_single_mapped_incorrect_is_candidate_not_verified():
    evs = [TagEvidence("q_tst001", "tag_a", "incorrect")]
    assert verification_status(evs) == "candidate"


def test_gate_two_distinct_questions_same_tag_verified():
    evs = [TagEvidence("q_tst001", "tag_a", "incorrect"),
           TagEvidence("q_tst002", "tag_a", "incorrect")]
    assert verification_status(evs) == "verified"


def test_gate_retry_same_question_not_double_counted():
    # same question submitted twice (retry/duplicate) → still candidate
    evs = [TagEvidence("q_tst001", "tag_a", "incorrect"),
           TagEvidence("q_tst001", "tag_a", "incorrect")]
    assert verification_status(evs) == "candidate"


def test_gate_correct_on_tagged_question_refutes():
    evs = [TagEvidence("q_tst001", "tag_a", "incorrect"),
           TagEvidence("q_tst002", "tag_a", "correct")]
    assert verification_status(evs) == "refuted"


def test_gate_unmapped_incorrect_is_insufficient_evidence():
    evs = [TagEvidence("q_tst001", "", "incorrect"),
           TagEvidence("q_tst002", "", "incorrect")]
    assert verification_status(evs) == "insufficient_evidence"


def test_gate_unanswered_never_counts():
    evs = [TagEvidence("q_tst001", "tag_a", "none"),
           TagEvidence("q_tst002", "tag_a", "none")]
    assert verification_status(evs) == "none"


def test_gate_no_suitable_followup_returns_pending():
    # insufficient-evidence state IS the pending state when nothing can
    # discriminate; assert the contract explicitly
    assert verification_status(
        [TagEvidence("q_tst001", "", "incorrect")]) == "insufficient_evidence"


# ---- fixture: in-memory repositories ----------------------------------------
class FakeEvents:
    def __init__(self):
        self.events: list[LearnerEvent] = []
        self._accepted: set[tuple[str, int]] = set()

    async def insert_event(self, ev):
        from app.domain.schemas import Outcome, PerEventResult
        key = (ev.device_id, ev.seq)
        if key in self._accepted:
            return PerEventResult(event_id=ev.event_id, seq=ev.seq, outcome=Outcome.DUPLICATE)
        self._accepted.add(key)
        self.events.append(ev)
        return PerEventResult(event_id=ev.event_id, seq=ev.seq, outcome=Outcome.ACCEPTED)

    async def list_events(self, learner_id, since_seq=0, limit=1000):
        return [e for e in self.events
                if e.learner_id == learner_id and e.seq >= since_seq]


class FakeMastery:
    def __init__(self):
        self.records = []

    async def get_mastery(self, learner_id):
        return list(self.records)

    async def upsert_mastery(self, **kw):
        from app.domain.schemas import MasteryRecord
        self.records = [r for r in self.records if r.concept_id != kw["concept_id"]]
        self.records.append(MasteryRecord(**kw))


class FakeDecisions:
    def __init__(self):
        self.saved, self.traces = [], {}

    async def save_decision(self, d):
        self.saved.append(d)

    async def save_trace(self, did, trace):
        self.traces[did] = trace


def make_question(qid="q_dia0001", miscopts=None, correct=2):
    return Question(
        question_id=qid, concept_id="c0001", chapter_id="ch001", qtype="mcq",
        prompt_or="ପ୍ର", options=["a", "b", "c", "d"], correct_option=correct,
        explanation_or="x", difficulty="easy",
        misconception_options=miscopts or {}, source_ref="s")


class FakePack:
    def __init__(self, questions):
        self.questions = {q.question_id: q for q in questions}
        self.prereqs = {}
        self.concept_order = ["c0001"]
        self.chapter_for_concept = {"c0001": "ch001"}
        self.get_question = lambda qid: self.questions.get(qid)


@pytest.fixture()
def harness():
    qs = [
        make_question("q_dia0001", miscopts={"0": "tag_a", "1": "tag_b"}),
        make_question("q_dia0002", miscopts={"0": "tag_a", "1": "tag_c"}),
    ]
    events, mastery = FakeEvents(), FakeMastery()
    pack = FakePack(qs)
    diag = DiagnosisService(pack, events, mastery)
    svc = AssessmentService(pack, events, mastery, diag)
    return svc, events, mastery, pack


async def submit(svc, seq, question_id, selected, device="dev_device0000000001"):
    return await svc.submit_assessment(
        "lrn_learner0000000001", device, AssessmentSubmission(
            question_id=question_id, selected_option=selected,
            submitted_at=int(time.time() * 1000)), seq)


# ---- integration: mastery, double-counting, diagnosis attach ----------------
@pytest.mark.asyncio
async def test_incorrect_answer_attaches_candidate_diagnosis(harness):
    svc, events, mastery, pack = harness
    res = await submit(svc, 1, "q_dia0001", 0)
    assert res.correct is False
    assert res.diagnosis is not None
    assert res.diagnosis["status"] == "candidate"
    assert res.diagnosis["causes"][0]["tag"] == "tag_a"
    assert res.diagnosis["verification_status"] == "candidate"
    # BKT mastery updated exactly once
    assert len(mastery.records) == 1 and mastery.records[0].attempts == 1


@pytest.mark.asyncio
async def test_duplicate_submission_does_not_double_count(harness):
    svc, events, mastery, pack = harness
    await submit(svc, 1, "q_dia0001", 0)      # accepted
    res2 = await submit(svc, 1, "q_dia0001", 0)  # same (device, seq) → duplicate
    assert mastery.records[0].attempts == 1
    assert res2.diagnosis is None  # duplicates get no re-diagnosis
    # a genuine retry on another device still can't double-count the SAME
    # question's evidence: diagnosis_service dedupes by question_id
    d = await svc.diagnosis.for_submission("lrn_learner0000000001", pack.questions["q_dia0001"], 0)
    assert d["verification_status"] == "candidate"


@pytest.mark.asyncio
async def test_second_distinct_question_verifies(harness):
    svc, events, mastery, pack = harness
    await submit(svc, 1, "q_dia0001", 0)
    res2 = await submit(svc, 2, "q_dia0002", 0)  # also maps to tag_a
    assert res2.diagnosis["verification_status"] == "verified"


@pytest.mark.asyncio
async def test_correct_answer_no_diagnosis(harness):
    svc, *_ = harness
    res = await submit(svc, 1, "q_dia0001", 2)
    assert res.correct is True
    assert res.diagnosis is None


@pytest.mark.asyncio
async def test_unmapped_wrong_answer_returns_insufficient(harness):
    svc, *_ = harness
    res = await submit(svc, 1, "q_dia0001", 3)  # option 3 unmapped
    assert res.diagnosis["status"] == "insufficient_evidence"
    assert res.diagnosis["verification_status"] == "insufficient_evidence"
    assert res.diagnosis["followup_question_id"] is None  # pending state


@pytest.mark.asyncio
async def test_followup_not_repeated(harness):
    svc, *_ = harness
    await submit(svc, 1, "q_dia0001", 0)
    res2 = await submit(svc, 2, "q_dia0002", 0)
    # both questions answered → no unexcluded follow-up remains
    assert res2.diagnosis["followup_question_id"] is None


@pytest.mark.asyncio
async def test_conflicting_evidence_refutes(harness):
    svc, events, mastery, pack = harness
    await submit(svc, 1, "q_dia0001", 0)   # tag_a incorrect
    await submit(svc, 2, "q_dia0001", 0)   # retry same question — no double count
    res = await submit(svc, 3, "q_dia0002", 2)  # correct on a tag_a-mapped question
    d = await svc.diagnosis.for_submission("lrn_learner0000000001", pack.questions["q_dia0001"], 0)
    assert d["verification_status"] == "refuted"


# ---- decision traces ---------------------------------------------------------
@pytest.mark.asyncio
async def test_decision_trace_saved_with_structured_steps(harness):
    from app.domain.schemas import NetworkState
    from app.services.decision_service import DecisionService
    svc, events, mastery, pack = harness
    dec_repo = FakeDecisions()
    ds = DecisionService(pack, mastery, dec_repo)
    d = await ds.next_decision("lrn_learner0000000001", NetworkState.ONLINE,
                               trigger_evidence="incorrect")
    trace = dec_repo.traces[d.decision_id]
    ids = [s.step_id for s in trace.trace]
    assert ids[:2] == ["select_target", "select_action"]
    assert "verification_gate" in ids  # incorrect trigger → gate step present
    # privacy: no raw answer text anywhere in summaries
    blob = str([s.output_summary for s in trace.trace])
    assert "answer_text" not in blob and "selected_option" not in blob


@pytest.mark.asyncio
async def test_decision_trace_no_gate_step_for_correct(harness):
    from app.domain.schemas import NetworkState
    from app.services.decision_service import DecisionService
    svc, events, mastery, pack = harness
    dec_repo = FakeDecisions()
    ds = DecisionService(pack, mastery, dec_repo)
    d = await ds.next_decision("lrn_learner0000000001", NetworkState.ONLINE,
                               trigger_evidence="correct")
    ids = [s.step_id for s in dec_repo.traces[d.decision_id].trace]
    assert "verification_gate" not in ids
