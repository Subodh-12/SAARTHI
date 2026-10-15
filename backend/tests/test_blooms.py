"""Tests for Bloom-aware question selection (Phase 4).

Proves Bloom metadata actually influences selection, that advanced levels
never override unresolved prerequisites, that legacy untagged questions
degrade gracefully, and that behavior is deterministic.
"""
import pytest

from app.domain.blooms import BLOOM_ORDER, bloom_window, select_question
from app.domain.schemas import Question

RULES = {"retry_threshold": 0.5, "advance_threshold": 0.85}


def mcq(qid: str, concept: str = "c0001", bloom: str | None = None,
        correct: int = 2) -> Question:
    return Question(
        question_id=qid, concept_id=concept, chapter_id="ch001", qtype="mcq",
        prompt_or="ପ୍ର", options=["a", "b", "c", "d"][:correct + 1 or 4],
        correct_option=correct, explanation_or="x", difficulty="easy",
        bloom_level=bloom, source_ref="s",
    )


# ---- prerequisite cap -------------------------------------------------------
def test_unresolved_prereqs_cap_window_at_understand():
    lo, hi = bloom_window(mastery_p=0.95, prereqs_resolved=False, ruleset_like=RULES)
    assert hi == BLOOM_ORDER["understand"]
    assert lo == BLOOM_ORDER["remember"]


def test_advanced_question_never_selected_when_prereqs_unresolved():
    qs = [mcq("q_easy01", bloom="remember"),
          mcq("q_adv001", bloom="analyze"),
          mcq("q_creat1", bloom="create")]
    qid, reason = select_question(qs, "c0001", mastery_p=0.95,
                                  prereqs_resolved=False, ruleset_like=RULES)
    assert qid == "q_easy01"
    assert reason == "question.bloom_in_window"


# ---- mastery widens the ceiling ----------------------------------------------
def test_low_mastery_stays_foundational():
    lo, hi = bloom_window(0.2, True, RULES)
    assert hi == BLOOM_ORDER["understand"]


def test_mid_mastery_unlocks_apply():
    lo, hi = bloom_window(0.6, True, RULES)
    assert hi == BLOOM_ORDER["apply"]


def test_high_mastery_unlocks_create():
    lo, hi = bloom_window(0.9, True, RULES)
    assert hi == BLOOM_ORDER["create"]


def test_selection_prefers_highest_allowed_level():
    qs = [mcq("q_rem001", bloom="remember"),
          mcq("q_app1001", bloom="apply"),
          mcq("q_und001", bloom="understand")]
    qid, _ = select_question(qs, "c0001", mastery_p=0.6, prereqs_resolved=True,
                             ruleset_like=RULES)
    assert qid == "q_app1001"  # apply is the most demanding allowed level


# ---- Bloom metadata actually matters ------------------------------------------
def test_bloom_metadata_changes_selection():
    qs = [mcq("q_rem001", bloom="remember"), mcq("q_eval001", bloom="evaluate")]
    low, _ = select_question(qs, "c0001", 0.3, True, ruleset_like=RULES)
    high, _ = select_question(qs, "c0001", 0.95, True, ruleset_like=RULES)
    assert low == "q_rem001"
    assert high == "q_eval001"


# ---- legacy questions without bloom -------------------------------------------
def test_legacy_untagged_questions_still_selected():
    qs = [mcq("q_legacy1"), mcq("q_legacy2")]
    qid, reason = select_question(qs, "c0001", 0.6, True, ruleset_like=RULES)
    assert qid == "q_legacy1"  # deterministic tie-break by id
    assert reason in ("question.bloom_in_window", "question.fallback_out_of_window")


def test_legacy_fallback_reason_explicit_when_window_narrow():
    # only a create-level question exists but learner is a novice → explicit fallback
    qs = [mcq("q_creat1", bloom="create")]
    qid, reason = select_question(qs, "c0001", 0.2, True, ruleset_like=RULES)
    assert qid == "q_creat1"
    assert reason == "question.fallback_out_of_window"


# ---- repetition ---------------------------------------------------------------
def test_excluded_questions_not_repeated_while_alternatives_exist():
    qs = [mcq("q_rep0001"), mcq("q_rep0002")]
    qid, _ = select_question(qs, "c0001", 0.6, True,
                             exclude_ids={"q_rep0001"}, ruleset_like=RULES)
    assert qid == "q_rep0002"


def test_repeat_is_explicit_when_nothing_else_available():
    qs = [mcq("q_only001")]
    qid, reason = select_question(qs, "c0001", 0.6, True,
                                  exclude_ids={"q_only001"}, ruleset_like=RULES)
    assert qid == "q_only001"
    assert reason == "question.repeat_only_available"


# ---- misc ----------------------------------------------------------------------
def test_other_concepts_ignored():
    qs = [mcq("q_other01", concept="c0002")]
    qid, reason = select_question(qs, "c0001", 0.6, True, ruleset_like=RULES)
    assert qid is None
    assert reason == "question.none_for_concept"


def test_short_answer_not_selected():
    q = Question(question_id="q_sa0001", concept_id="c0001", chapter_id="ch001",
                 qtype="short_answer", prompt_or="ପ୍ର", options=[],
                 explanation_or="x", difficulty="easy", source_ref="s")
    assert select_question([q], "c0001", 0.6, True, ruleset_like=RULES)[0] is None


def test_deterministic():
    qs = [mcq("q_det0002", bloom="apply"), mcq("q_det0001", bloom="apply")]
    a = select_question(qs, "c0001", 0.6, True, ruleset_like=RULES)
    b = select_question(list(reversed(qs)), "c0001", 0.6, True, ruleset_like=RULES)
    assert a == b


def test_invalid_bloom_in_pack_data_is_rejected():
    with pytest.raises(Exception):
        Question(question_id="q_badblm", concept_id="c0001", chapter_id="ch001",
                 qtype="mcq", prompt_or="x", options=["a"], correct_option=0,
                 explanation_or="x", difficulty="easy", bloom_level="expert",
                 source_ref="s")
