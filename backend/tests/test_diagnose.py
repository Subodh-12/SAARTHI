"""Tests for cause-aware misconception diagnosis (Phase 3).

Covers: known causes, competing causes, missing tags (insufficient evidence),
ambiguity/unsupported questions, follow-up discrimination and determinism,
unanswered-not-incorrect, and pending-teacher-review flagging.
"""
import pytest

from app.domain.diagnose import (
    MISCONCEPTION_CATALOG,
    diagnose_concept,
    diagnose_submission,
    select_followup,
)
from app.domain.schemas import Question


def mcq(qid: str, concept: str = "c0001", correct: int = 2,
        options: int = 4, miscopts: dict | None = None,
        mtag: str | None = None) -> Question:
    tail = qid[2:] if qid.startswith("q_") else qid
    qid = "q_" + tail.zfill(6)  # ensure the QuestionId pattern (min 6 tail chars)
    return Question(
        question_id=qid, concept_id=concept, chapter_id="ch001", qtype="mcq",
        prompt_or="ପ୍ରଶ୍ନ", options=[f"opt{i}" for i in range(options)],
        correct_option=correct, explanation_or="ବ୍ୟାଖ୍ୟା", difficulty="easy",
        misconception_tag=mtag,
        misconception_options=miscopts or {},
        source_ref="ch01 §1.2",
    )


# ---- known cause ----------------------------------------------------------
def test_known_cause_produces_candidate_with_catalog_label():
    q = mcq("q1", miscopts={"1": "relative_density_float"})
    d = diagnose_submission(q, selected_option=1)
    assert d.status == "candidate"
    assert len(d.causes) == 1
    c = d.causes[0]
    assert c.tag == "relative_density_float"
    assert c.pending_teacher_review is False
    assert c.label_en == MISCONCEPTION_CATALOG["relative_density_float"]["label_en"]
    assert c.supporting and not c.contradicting
    assert d.followup_question_id is None  # no concept questions given


def test_correct_answer_yields_no_cause():
    q = mcq("q1", correct=2, miscopts={"1": "relative_density_float"})
    assert diagnose_submission(q, selected_option=2).status == "correct"


def test_prereq_success_recorded_as_contradicting_evidence():
    q = mcq("q1", miscopts={"1": "relative_density_float"})
    d = diagnose_submission(q, selected_option=1, prereq_correct_recently=True)
    assert d.causes[0].contradicting


# ---- competing causes -------------------------------------------------------
def test_competing_causes_merged_and_discriminating_followup_selected():
    q1 = mcq("q_c0001_01", miscopts={"0": "tag_a", "1": "tag_b"})
    q2 = mcq("q_c0001_02", miscopts={"0": "tag_a", "1": "tag_c"})
    q3 = mcq("q_c0001_03", miscopts={"0": "tag_a", "1": "tag_b"})
    d = diagnose_concept([(q1, 0), (q2, 1)], concept_questions=[q1, q2, q3])
    assert d.status == "candidate"
    tags = [c.tag for c in d.causes]
    assert tags == ["tag_a", "tag_c"]  # deterministic ascending order
    assert "distinguish" in d.note_en
    # q3's mapping contains exactly one candidate tag (tag_a) and q3 was not answered
    assert d.followup_question_id == "q_c0001_03"


def test_competing_causes_followup_never_repeats_answered_question():
    q1 = mcq("q_rep001", miscopts={"0": "tag_a", "1": "tag_b"})
    q2 = mcq("q_rep002", miscopts={"0": "tag_a", "1": "tag_c"})
    q3 = mcq("q_rep003", miscopts={"0": "tag_a", "1": "tag_c"})
    # every pool question is excluded (answered) → no follow-up, no repetition
    d = diagnose_concept([(q1, 0), (q2, 1)],
                         recently_answered={"q_rep001", "q_rep002", "q_rep003"},
                         concept_questions=[q1, q2, q3])
    assert d.followup_question_id is None


# ---- missing tags / insufficient evidence -----------------------------------
def test_missing_tag_mapping_is_insufficient_not_invented():
    q = mcq("q1")
    d = diagnose_submission(q, selected_option=1)
    assert d.status == "insufficient_evidence"
    assert d.causes == []


def test_unmapped_incorrect_in_concept_merge_is_insufficient():
    q1 = mcq("q_nomap1")
    q2 = mcq("q_nomap2")
    d = diagnose_concept([(q1, 1), (q2, 3)])
    assert d.status == "insufficient_evidence"


def test_unknown_tag_flagged_pending_teacher_review():
    q = mcq("q1", mtag="invented_tag")
    d = diagnose_submission(q, selected_option=1)
    assert d.status == "candidate"
    assert d.causes[0].pending_teacher_review is True
    assert d.causes[0].tag == "invented_tag"


# ---- ambiguity / unsupported ------------------------------------------------
def test_short_answer_is_unsupported():
    q = Question(question_id="q_sa0001", concept_id="c0001", chapter_id="ch001",
                 qtype="short_answer", prompt_or="ପ୍ର", options=[],
                 explanation_or="x", difficulty="easy", source_ref="s")
    assert diagnose_submission(q, selected_option=None).status == "unsupported"


def test_unanswered_is_not_incorrect():
    q = mcq("q1", miscopts={"1": "relative_density_float"})
    d = diagnose_submission(q, selected_option=None)
    assert d.status == "unsupported"
    assert "unanswered is not counted" in d.note_en


def test_unanswered_excluded_from_concept_evidence():
    q1 = mcq("q_unans1", miscopts={"0": "tag_a"})
    q2 = mcq("q_unans2", miscopts={"0": "tag_a"})
    d = diagnose_concept([(q1, 0), (q2, None)])  # q2 unanswered
    assert d.status == "candidate"
    assert all("q_02" not in ev for c in d.causes for ev in c.supporting)


def test_no_responses_insufficient():
    assert diagnose_concept([]).status == "insufficient_evidence"


# ---- determinism ------------------------------------------------------------
def test_diagnosis_is_deterministic():
    q = mcq("q1", miscopts={"1": "relative_density_float"})
    d1 = diagnose_submission(q, selected_option=1)
    d2 = diagnose_submission(q, selected_option=1)
    assert d1 == d2


def test_select_followup_tie_breaks_by_question_id():
    qs = [mcq("q_tiebb1"), mcq("q_tieaa1")]
    assert select_followup([], qs) == "q_tieaa1"


def test_select_followup_prefers_discriminating_over_neutral():
    disc = mcq("q_disc01", miscopts={"0": "tag_a", "1": "tag_b"})
    neutral = mcq("q_neut01")
    assert select_followup(["tag_a"], [neutral, disc]) == "q_disc01"


# ---- schema/back-compat -------------------------------------------------------
def test_question_without_mapping_loads_with_empty_dict():
    q = Question(question_id="q_none01", concept_id="c0001", chapter_id="ch001",
                 qtype="mcq", prompt_or="ପ୍ର", options=["a", "b"],
                 correct_option=0, explanation_or="x", difficulty="easy",
                 source_ref="s")
    assert q.misconception_options == {}
