"""Regression tests for the Doubt Relay defects D1, D2, D3 and the
language-independent classification contract.

D1: correct Odia answers were classified as insufficient (English-only keywords).
D2: identical wrong answers were classified as insufficient (0 keyword hits
    collapsed into insufficient instead of agree_incorrect).
D3: unmatched questions silently fell back to RELAY_BANK[0].
"""
import asyncio

import pytest

from app.services.rooms_agent import DemoKaranaAgent
from app.services.rooms_content import RELAY_BANK

EVAP_Q = RELAY_BANK[0]["question"]  # "Why does sweat cool our body..."


@pytest.fixture()
def agent() -> DemoKaranaAgent:
    return DemoKaranaAgent()


def resolve(agent, question, contents, **kw):
    subs = [{"content": c} for c in contents]
    return asyncio.run(agent.resolve_relay(question, subs, **kw))


# ---- D1: Odia correct answers ------------------------------------------
def test_d1_correct_odia_answers_classified_agree(agent):
    r = resolve(agent, EVAP_Q, [
        "ପରିବାହୀନତା ପାଇଁ ମୁଣ୍ଡା ଗରମ ହୋଇ ପାଣି ବାଷ୍ପୀଭବନ ହୋଇ ଶରୀରର ତାପ ନେଇନିଏ।",
        "ଯେତେବେଳେ ଝାଳ ବାଷ୍ପୀଭବନ ହୁଏ, ଏହା ଲୁଚ୍ଚ ତାପ ନେଇ ଚର୍ମ ଥଣ୍ଡା କରେ।",
    ])
    assert r["pattern"] == "agree", r
    assert r["bank_id"] == "rel-matter-evaporation"
    assert r["proceed_to_verification"] is True


def test_d1_mixed_odia_and_english_correct(agent):
    r = resolve(agent, EVAP_Q, [
        "Evaporation removes latent heat from the skin.",
        "ଝାଳ ବାଷ୍ପୀଭବନ ହୋଇ ତାପ ନେଇନିଏ।",
    ])
    assert r["pattern"] == "agree"


# ---- D2: identical wrong answers ----------------------------------------
def test_d2_identical_wrong_answers_agree_incorrect(agent):
    r = resolve(agent, EVAP_Q, [
        "sweat is cold water so it cools the skin directly",
        "sweat is cold water so it cools the skin directly",
    ])
    assert r["pattern"] == "agree_incorrect", r
    # agreement on a wrong answer is NOT a diagnosed misconception
    assert "not a diagnosed misconception" in r["followup"]["text"] or \
        "shared gap" in r["followup"]["text"]
    assert r["proceed_to_verification"] is True


def test_d2_identical_wrong_odia_answers_agree_incorrect(agent):
    r = resolve(agent, EVAP_Q, [
        "ଝାଳ ଥଣ୍ଡା ପାଣି ଅଟେ ତେଣୁ ଚର୍ମ ଥଣ୍ଡା ହୁଏ ସିଧାସଳଖ",
        "ଝାଳ ଥଣ୍ଡା ପାଣି ଅଟେ ତେଣୁ ଚର୍ମ ଥଣ୍ଡା ହୁଏ ସିଧାସଳଖ",
    ])
    assert r["pattern"] == "agree_incorrect"


def test_agree_correct_distinct_from_agree_incorrect(agent):
    good = resolve(agent, EVAP_Q, ["evaporation of sweat", "evaporate removes heat"])
    bad = resolve(agent, EVAP_Q, ["sweat is cold water", "sweat is cold water"])
    assert good["pattern"] == "agree"
    assert bad["pattern"] == "agree_incorrect"
    assert good["followup"]["text"] != bad["followup"]["text"]


# ---- D3: unmatched question ---------------------------------------------
def test_d3_unmatched_question_returns_unmatched_not_fallback(agent):
    r = resolve(agent, "What is the chemical formula of ozone?", [
        "ozone is O3 with three oxygen atoms",
        "ozone has three oxygen atoms bonded",
    ])
    assert r["pattern"] == "unmatched", r
    assert r["bank_id"] is None
    assert r["expected_answer"] is None
    assert r["proceed_to_verification"] is False
    assert r["verification"] is None
    # no unrelated bank answer is imposed
    assert r["explanation"] is None


def test_d3_weak_token_overlap_is_not_a_match(agent):
    # single generic word overlap must not select an unrelated item
    r = resolve(agent, "What is water made of?", [
        "water is made of hydrogen and oxygen",
        "hydrogen and oxygen form water",
    ])
    assert r["pattern"] == "unmatched"


# ---- explicit edge cases -------------------------------------------------
def test_single_submission_insufficient(agent):
    r = resolve(agent, EVAP_Q, ["evaporation cools the skin a lot"])
    assert r["pattern"] == "insufficient"


def test_empty_and_too_short_submissions_insufficient(agent):
    r = resolve(agent, EVAP_Q, ["", "too short"])
    assert r["pattern"] == "insufficient"


def test_disagree_mixed_correctness(agent):
    r = resolve(agent, EVAP_Q, [
        "evaporation takes latent heat from the skin",
        "the fan blows cold air onto the skin directly",
    ])
    assert r["pattern"] == "disagree"


# ---- stable ID preference -------------------------------------------------
def test_bank_item_id_beats_fuzzy_match(agent):
    r = resolve(agent, "random unrelated question text here",
                ["protein-rich plasma stays in blood", "lymph lacks proteins"],
                bank_item_id="rel-cell-plasma")
    assert r["bank_id"] == "rel-cell-plasma"


def test_bank_id_embedded_in_question(agent):
    r = resolve(agent, "rel-motion-distance — discuss",
                ["distance can never be less than displacement", "never possible"])
    assert r["bank_id"] == "rel-motion-distance"


def test_known_bank_item_id_none_falls_back_to_matching(agent):
    r = resolve(agent, EVAP_Q, ["evaporation cools us", "evaporation again"],
                bank_item_id=None)
    assert r["bank_id"] == "rel-matter-evaporation"


def test_every_pattern_has_trace_and_unresolved(agent):
    for contents in (["evaporation cools", "evaporation works"],
                     ["cold water", "cold water"],
                     ["evaporation cools", "cold water"],
                     ["x", "y"]):
        r = resolve(agent, EVAP_Q, contents)
        assert isinstance(r["trace"], list) and r["trace"]
        assert isinstance(r["unresolved"], list)
