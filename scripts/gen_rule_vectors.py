"""Generate shared test vectors for the v2 deterministic decision engine.

Produces `tests/fixtures/rule_vectors.json` consumed by BOTH the Python
test suite (`backend/tests/test_decide_vectors.py`) and the TypeScript
suite (`frontend/tests/decide.test.ts`) — Design v2 Section 15
"Cross-language parity".

Contents:
  - `golden`  : hand-labelled scenario vectors. Expected outputs are
                asserted HERE against the Python engine before the file is
                written, so the generator fails loudly if the engine
                violates the labelled expectation (not just snapshots).
  - `fuzz`    : engine-generated regression vectors (snapshot of the
                current engine on deterministic pseudo-random inputs).
  - `bkt`     : step-by-step BKT update sequences in basis points, incl.
                clamping and half-up rounding cases.
  - `invalid` : invalid-field inputs where the fallback decision
                (STATE_INVALID_FALLBACK) is expected in BOTH engines.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.domain.bkt import bkt_update_bp, mastery_band_bp  # type: ignore
from app.domain.decide import (  # type: ignore
    DecisionInput, MasteryEntry, RecentEvent, decide,
)
from app.domain.ruleset import get_ruleset, reset_ruleset_cache  # type: ignore

REPO = Path(__file__).resolve().parent.parent
RULESET_PATH = REPO / "packages" / "ruleset" / "rules.json"

REASON_MESSAGES: dict[str, str] = {
    "STATE_INVALID_FALLBACK": "ଅସ୍ଥାୟୀ ସମସ୍ୟା। ପୁଣି ଚେଷ୍ଟା କର।",
    "COLD_START": "ପ୍ରଥମ ଧାରଣା ଆରମ୍ଭ କର।",
    "WEAK_PREREQ_GAP": "ପ୍ରଥମେ ଆଧାର ଧାରଣା ବଦ୍ଧ କର।",
    "WEAK_CONCEPT": "ଏହି ଧାରଣା ପୁଣି ଶିଖ।",
    "WRONG_RETRY": "ଉତ୍ତର ଭୁଲ ଥିଲା। ପୁଣି ଚେଷ୍ଟା କର।",
    "PARTIAL_PRACTICE": "ଭଲ ହେଲା! ଆଉ ଏକ ଅଭ୍ୟାସ କର।",
    "MASTERED_ADVANCE": "ବାହ୍! ପରବର୍ତ୍ତୀ ଧାରଣା କୁ ଯାଅ।",
    "NO_GAIN_ALT_CONTENT": "ଅନ୍ୟ ଉପାୟରେ ପାଠ ପଢ।",
    "NO_GAIN_REMEDIATE_PREREQ": "ପ୍ରଥମେ ଆଧାର ଧାରଣା ବଦ୍ଧ କର।",
    "INTERVENTIONS_EXHAUSTED": "ଶିକ୍ଷକଙ୍କ ସହିତ ଯୋଗାଯୋଗ କର।",
    "SLICE_COMPLETE": "ସମସ୍ତ ପାଠ ସମ୍ପୂର୍ଣ୍ଣ! ପୁଣି ରିଭିଜନ୍ କର।",
    "BLOCKED_BY_PREREQ": "ପ୍ରଥମେ ଆଧାର ଧାରଣା ଶିଖ।",
    "CONTENT_NOT_AVAILABLE_OFFLINE": "ଏହି ପାଠ ଅଫଲାଇନ୍ ଉପଲବ୍ଧ ନାହିଁ। ଅନ୍ୟ ପାଠ ପଢ।",
}

reset_ruleset_cache()
RULESET = get_ruleset(str(RULESET_PATH))

# Deterministic concept graph: c0001..c0006 across two chapters.
#   c0001 ← c0002 ← c0004      (prerequisite direction)
#   c0003 ← c0005
#   c0006 standalone
ORDER = ["c0001", "c0002", "c0003", "c0004", "c0005", "c0006"]
CHAPTER = {"c0001": "ch001", "c0002": "ch001", "c0003": "ch001",
           "c0004": "ch002", "c0005": "ch002", "c0006": "ch002"}
PREREQS = {"c0002": ["c0001"], "c0004": ["c0002"], "c0005": ["c0003"],
           "c0001": [], "c0003": [], "c0006": []}
PACK = "pack_class9_ch1"
PACK2 = "pack_class9_ch2"
# Two chapter-scoped packs so the offline-missing-pack substitution has a
# target: c0001-c0003 live in pack_ch1, c0004-c0006 in pack_ch2.
PACKS = {**{cid: PACK for cid in ORDER[:3]}, **{cid: PACK2 for cid in ORDER[3:]}}


def _inp(**over) -> dict:
    base = {
        "trigger_event_type": "SESSION_STARTED",
        "trigger_concept_id": None,
        "trigger_correct": None,
        "mastery": {},
        "recent_events": [],
        "prereqs": PREREQS,
        "concept_order": ORDER,
        "chapter_id_for_concept": CHAPTER,
        "doubt_concept_hint": None,
        "env_network": "online",
        "installed_pack_versions": {PACK: 1},
        "required_pack_for_concept": PACKS,
        "storage_free_mb": 500,
        "battery_saver": False,
        "outbox_nonempty": False,
        "ruleset_version": RULESET.ruleset_version,
        "bloom_mastery": {},
        "available_bloom_levels_for_concept": {},
    }
    base.update(over)
    return base


def _m(p: int, attempts: int = 0, correct: int = 0) -> dict:
    return {"p_bp": p, "attempts": attempts, "correct": correct,
            "last_event_seq": 0}


def _graded(seq: int, cid: str, correct: bool, p_after: int,
            last_action: str | None = None) -> dict:
    return {"seq": seq, "event_type": "ANSWER_SUBMITTED", "concept_id": cid,
            "correct": correct, "p_bp_after": p_after,
            "last_action": last_action}


def _decision(seq: int, cid: str, action: str) -> dict:
    return {"seq": seq, "event_type": "DECISION_MADE_LOCAL", "concept_id": cid,
            "correct": None, "p_bp_after": None, "last_action": action}


# --------------------------------------------------------------------------- #
# Golden, hand-labelled scenarios (v2 Section 6 + Appendix A)
# --------------------------------------------------------------------------- #
GOLDEN: list[tuple[str, dict, dict]] = []


def _golden(name, inp, action, target, reason, needs_help=False,
            delivery=None, background=None, target_bloom=None):
    expected = {
        "action": action,
        "target_concept_id": target,
        "reason_code": reason,
        "needs_help": needs_help,
    }
    if delivery is not None:
        expected["delivery_mode"] = delivery
    if background is not None:
        expected["background_actions"] = background
    if target_bloom is not None:
        expected["target_bloom_level"] = target_bloom
    GOLDEN.append((name, inp, expected))


# 1. Cold start: no mastery rows → ADVANCE to first concept without prereqs.
_golden("cold_start", _inp(), "ADVANCE", "c0001", "COLD_START")

# 2. No concepts available at all (corrupt/empty slice) → safe fallback.
#    (A coherent installed slice is a DAG, so a cold start with every
#    concept carrying in-slice prerequisites cannot occur; an incoherent
#    graph with out-of-slice prereq targets fails the trajectory check and
#    lands in the same fallback.)
_golden("no_concepts_available",
        _inp(concept_order=[]),
        "RETRY", "", "STATE_INVALID_FALLBACK")

# 3. Weak concept + weak prereq → REMEDIATE the weakest prerequisite.
_golden("weak_prereq_gap",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0002",
             trigger_correct=False,
             mastery={"c0001": _m(3000), "c0002": _m(2500)}),
        "REMEDIATE", "c0001", "WEAK_PREREQ_GAP")

# 4. Weak concept, prereqs fine → REMEDIATE the target.
_golden("weak_concept",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=False, mastery={"c0001": _m(3500)}),
        "REMEDIATE", "c0001", "WEAK_CONCEPT")

# 5. Partial mastery, last graded wrong → RETRY (WRONG_RETRY).
_golden("wrong_retry",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=False, mastery={"c0001": _m(5000, 2, 0)},
             recent_events=[_graded(1, "c0001", False, 5000)]),
        "RETRY", "c0001", "WRONG_RETRY")

# 6. Partial mastery, last graded correct → RETRY (PARTIAL_PRACTICE).
_golden("partial_practice",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=True, mastery={"c0001": _m(6000, 2, 1)},
             recent_events=[_graded(1, "c0001", True, 6000)]),
        "RETRY", "c0001", "PARTIAL_PRACTICE")

# 7. Mastered target → ADVANCE to next eligible.
_golden("mastered_advance",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=True,
             mastery={"c0001": _m(9000, 5, 5), "c0002": _m(1000)}),
        "ADVANCE", "c0002", "MASTERED_ADVANCE")

# 8. Guard step 1: 3 answers without gain, no alt content yet → REVISE alt.
_golden("guard_alt_content",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=False,
             mastery={"c0001": _m(4100, 4, 0)},
             recent_events=[_graded(1, "c0001", False, 4050),
                            _graded(2, "c0001", False, 4080),
                            _graded(3, "c0001", False, 4100)]),
        "REVISE", "c0001", "NO_GAIN_ALT_CONTENT")

# 9. Guard step 2: alt content shown, prereq weak → REMEDIATE prereq.
_golden("guard_remediate_prereq",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0002",
             trigger_correct=False,
             mastery={"c0001": _m(3800, 2, 1), "c0002": _m(5000, 4, 1)},
             recent_events=[_graded(1, "c0002", False, 4980),
                            _decision(2, "c0002", "REVISE"),
                            _graded(3, "c0002", False, 4990),
                            _graded(4, "c0002", False, 5000)]),
        "REMEDIATE", "c0001", "NO_GAIN_REMEDIATE_PREREQ")

# 10. Guard step 3: interventions exhausted → terminal REVISE + needs_help.
_golden("guard_interventions_exhausted",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=False,
             mastery={"c0001": _m(4200, 4, 0)},
             recent_events=[_graded(1, "c0001", False, 4150),
                            _decision(2, "c0001", "REVISE"),
                            _graded(3, "c0001", False, 4180),
                            _graded(4, "c0001", False, 4200)]),
        "REVISE", "c0001", "INTERVENTIONS_EXHAUSTED", needs_help=True)

# 11. Guard NEVER advances a below-mastered target: the terminal state keeps
#     the learner on T even when other concepts exist.
_golden("guard_never_advances",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=False,
             mastery={"c0001": _m(4200, 4, 0), "c0002": _m(9000, 9, 9)},
             recent_events=[_graded(1, "c0001", False, 4150),
                            _decision(2, "c0001", "REVISE"),
                            _graded(3, "c0001", False, 4180),
                            _graded(4, "c0001", False, 4200)]),
        "REVISE", "c0001", "INTERVENTIONS_EXHAUSTED", needs_help=True)

# 12. Slice complete: every concept mastered → REVISE oldest last-seen.
_golden("slice_complete",
        _inp(trigger_event_type="SESSION_STARTED",
             mastery={cid: _m(9000, 5, 5) for cid in ORDER}),
        "REVISE", "c0001", "SLICE_COMPLETE")

# 13. Mastered target, next concept partially eligible → ADVANCE to it.
#     (In a coherent DAG slice some unmastered concept always has mastered
#     prerequisites, so a fully blocked advance can only arise from an
#     incoherent graph, which fails the trajectory check into the fallback;
#     the engine keeps the v2 BLOCKED_BY_PREREQ branch as defence.)
_golden("mastered_advance_to_partial_next",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=True,
             mastery={"c0001": _m(9000, 5, 5), "c0002": _m(8600, 4, 4),
                      "c0003": _m(2000, 1, 0)}),
        "ADVANCE", "c0003", "MASTERED_ADVANCE")

# 14. Missing pack offline → nearest installed concept (by graph distance,
#     ties by chapter order) + CONTENT_NOT_AVAILABLE_OFFLINE.
#     c0001's pack is absent; pack_ch2 (c0004-c0006) is installed. Nearest
#     installed: c0004 (distance 2 via c0002), chapter order before c0005.
_golden("content_not_available_offline",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=False,
             mastery={"c0001": _m(3000)},
             env_network="offline",
             installed_pack_versions={"pack_class9_ch2": 1},
             required_pack_for_concept=PACKS),
        "REMEDIATE", "c0004", "CONTENT_NOT_AVAILABLE_OFFLINE",
        delivery="cached", background=[])

# 14b. No pack installed at all → fallback decision (v2 edge behaviour).
_golden("no_pack_installed_offline",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=False,
             mastery={"c0001": _m(3000)},
             env_network="offline",
             installed_pack_versions={},
             required_pack_for_concept=PACKS),
        "RETRY", "c0001", "STATE_INVALID_FALLBACK", delivery="cached")

# 15. Invalid state: out-of-range mastery → fallback RETRY on last concept.
_golden("state_invalid_fallback",
        _inp(trigger_concept_id="c0001",
             mastery={"c0001": _m(12000)}),
        "RETRY", "c0001", "STATE_INVALID_FALLBACK")

# 16. Unknown ruleset version → typed-error situation, fallback decision.
_golden("unknown_ruleset_fallback",
        _inp(ruleset_version="9.9.9"),
        "ADVANCE", "c0001", "STATE_INVALID_FALLBACK")

# 17. Doubt concept hint selects the target when no graded answer exists.
_golden("doubt_hint_target",
        _inp(trigger_event_type="DOUBT_ASKED",
             doubt_concept_hint="c0003",
             mastery={"c0001": _m(5000, 2, 1), "c0003": _m(5000, 2, 1)}),
        "RETRY", "c0003", "PARTIAL_PRACTICE")

# 18. Delivery: offline always cached; online with outbox → SYNC background.
_golden("delivery_offline_cached",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=False, mastery={"c0001": _m(3500)},
             env_network="offline", outbox_nonempty=True),
        "REMEDIATE", "c0001", "WEAK_CONCEPT",
        delivery="cached", background=[])

_golden("delivery_online_sync",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=False, mastery={"c0001": _m(3500)},
             env_network="online", outbox_nonempty=True,
             installed_pack_versions={}),
        "REMEDIATE", "c0001", "WEAK_CONCEPT",
        delivery="prefetch_then_offline", background=["PREFETCH", "SYNC"])
# 19. Prefetch blocked by battery saver / low storage.
_golden("prefetch_blocked_battery_saver",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=False, mastery={"c0001": _m(3500)},
             env_network="online", battery_saver=True,
             installed_pack_versions={}),
        "REMEDIATE", "c0001", "WEAK_CONCEPT",
        delivery="prefetch_then_offline", background=[])

# 20. Boundary: exactly at mastered threshold (8500) → ADVANCE.
_golden("boundary_mastered_at_8500",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=True, mastery={"c0001": _m(8500, 5, 5),
                                            "c0002": _m(0)}),
        "ADVANCE", "c0002", "MASTERED_ADVANCE")

# 21. Boundary: exactly at weak threshold (4000) → partial band → RETRY.
_golden("boundary_weak_at_4000",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=True, mastery={"c0001": _m(4000, 1, 1)}),
        "RETRY", "c0001", "PARTIAL_PRACTICE", target_bloom="remember")

# 22. Bloom progression: foundational mastery (remember >= 7000) advances target to understand.
_golden("bloom_progress_to_understand",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=True, mastery={"c0001": _m(7200, 3, 2)},
             bloom_mastery={"c0001": {"remember": _m(7500, 2, 2), "understand": _m(2000, 1, 0)}}),
        "RETRY", "c0001", "PARTIAL_PRACTICE", target_bloom="understand")

# 23. Bloom progression: foundational demonstrated (remember & understand >= 7000) advances target to apply.
_golden("bloom_progress_to_apply",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=True, mastery={"c0001": _m(7800, 5, 4)},
             bloom_mastery={"c0001": {"remember": _m(8000, 2, 2), "understand": _m(7500, 2, 2), "apply": _m(2000, 1, 0)}}),
        "RETRY", "c0001", "PARTIAL_PRACTICE", target_bloom="apply")

# 24. Bloom safe fallback: higher level wanted but unavailable for concept → fallback to highest available.
_golden("bloom_fallback_when_higher_level_unavailable",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=True, mastery={"c0001": _m(7800, 5, 4)},
             bloom_mastery={"c0001": {"remember": _m(8000, 2, 2), "understand": _m(7500, 2, 2)}},
             available_bloom_levels_for_concept={"c0001": ["remember", "understand"]}),
        "RETRY", "c0001", "PARTIAL_PRACTICE", target_bloom="understand")

# 25. Bloom remediation anchors back to foundational level below proficiency.
_golden("bloom_remediate_anchors_foundational",
        _inp(trigger_event_type="ANSWER_SUBMITTED", trigger_concept_id="c0001",
             trigger_correct=False, mastery={"c0001": _m(3500, 3, 0)},
             bloom_mastery={"c0001": {"remember": _m(3500, 3, 0), "understand": _m(2000, 0, 0)}}),
        "REMEDIATE", "c0001", "WEAK_CONCEPT", target_bloom="remember")


def _canonical(inp: dict) -> dict:
    """Deterministic canonical form shared by both engines."""
    return {
        "trigger_event_type": inp["trigger_event_type"],
        "trigger_concept_id": inp["trigger_concept_id"],
        "trigger_correct": inp["trigger_correct"],
        "mastery": {k: dict(v) for k, v in inp["mastery"].items()},
        "recent_events": [dict(e) for e in inp["recent_events"]],
        "prereqs": inp["prereqs"],
        "concept_order": inp["concept_order"],
        "chapter_id_for_concept": inp["chapter_id_for_concept"],
        "doubt_concept_hint": inp["doubt_concept_hint"],
        "env_network": inp["env_network"],
        "installed_pack_versions": inp["installed_pack_versions"],
        "required_pack_for_concept": inp["required_pack_for_concept"],
        "storage_free_mb": inp["storage_free_mb"],
        "battery_saver": inp["battery_saver"],
        "outbox_nonempty": inp["outbox_nonempty"],
        "ruleset_version": inp["ruleset_version"],
        "bloom_mastery": {k: {bl: dict(bm) for bl, bm in v.items()}
                          for k, v in inp.get("bloom_mastery", {}).items()},
        "available_bloom_levels_for_concept": {k: list(v)
                                               for k, v in inp.get("available_bloom_levels_for_concept", {}).items()},
    }


def _to_decision_input(d: dict) -> DecisionInput:
    bloom_mastery = {
        cid: {
            lvl: MasteryEntry(p_bp=bm["p_bp"], attempts=bm.get("attempts", 0),
                              correct=bm.get("correct", 0),
                              last_event_seq=bm.get("last_event_seq", 0))
            for lvl, bm in levels.items()
        }
        for cid, levels in d.get("bloom_mastery", {}).items()
    }
    return DecisionInput(
        trigger_event_type=d["trigger_event_type"],
        trigger_concept_id=d["trigger_concept_id"],
        trigger_correct=d["trigger_correct"],
        mastery={k: MasteryEntry(p_bp=v["p_bp"], attempts=v.get("attempts", 0),
                                 correct=v.get("correct", 0),
                                 last_event_seq=v.get("last_event_seq", 0))
                 for k, v in d["mastery"].items()},
        recent_events=[RecentEvent(seq=e["seq"], event_type=e["event_type"],
                                   concept_id=e.get("concept_id"),
                                   correct=e.get("correct"),
                                   p_bp_after=e.get("p_bp_after"),
                                   last_action=e.get("last_action"))
                       for e in d["recent_events"]],
        prereqs=d["prereqs"],
        concept_order=d["concept_order"],
        chapter_id_for_concept=d["chapter_id_for_concept"],
        doubt_concept_hint=d["doubt_concept_hint"],
        env_network=d["env_network"],
        installed_pack_versions=d["installed_pack_versions"],
        required_pack_for_concept=d["required_pack_for_concept"],
        storage_free_mb=d["storage_free_mb"],
        battery_saver=d["battery_saver"],
        outbox_nonempty=d["outbox_nonempty"],
        ruleset_version=d["ruleset_version"],
        bloom_mastery=bloom_mastery,
        available_bloom_levels_for_concept=d.get("available_bloom_levels_for_concept", {}),
    )


# Validate golden vectors against the engine BEFORE writing the file.
golden_vectors = []
for name, inp, expected in GOLDEN:
    out = decide(_to_decision_input(inp), RULESET, REASON_MESSAGES)
    actual = {
        "action": out.action,
        "target_concept_id": out.target_concept_id,
        "reason_code": out.reason_code,
        "target_bloom_level": out.target_bloom_level,
        "needs_help": out.needs_help,
        "delivery_mode": out.delivery_mode,
        "background_actions": out.background_actions,
    }
    for key, want in expected.items():
        got = actual[key]
        assert got == want, (
            f"golden vector {name!r}: engine returned {key}={got!r}, "
            f"hand label expects {want!r} (full output: {actual})")
    golden_vectors.append({
        "name": name,
        "input": _canonical(inp),
        "expected": actual,
    })

# --------------------------------------------------------------------------- #
# BKT sequences (step-by-step in basis points; Appendix A)
# --------------------------------------------------------------------------- #
bkt_cases: list[dict] = []


def _bkt_case(name: str, p0: int, answers: list[bool]) -> None:
    p = p0
    steps = []
    for correct in answers:
        p = bkt_update_bp(p, correct, RULESET)
        steps.append({"correct": correct, "p_bp": p,
                      "band": mastery_band_bp(p, RULESET)})
    bkt_cases.append({"name": name, "p_init_bp": p0,
                      "answers": answers, "steps": steps})


_bkt_case("correct_from_init", 2000, [True])
_bkt_case("wrong_from_init", 2000, [False])
_bkt_case("two_correct", 2000, [True, True])
_bkt_case("correct_wrong_correct", 2000, [True, False, True])
_bkt_case("repeated_wrong_clamp", 2000, [False, False, False, False, False])
_bkt_case("repeated_correct_clamp", 2000, [True, True, True, True, True, True])
_bkt_case("from_clamp_low", 100, [True])
_bkt_case("from_clamp_high", 9900, [False])
_bkt_case("half_up_odd_value", 3333, [True])
_bkt_case("half_up_boundary", 2500, [True])

# Hand-verified first-step value (exact rational arithmetic, Appendix A):
# P=2000, correct → posterior = (2000·9000)/(2000·9000 + 8000·2000) = 9/17;
# p_next = 9/17 + (8/17)·0.15 = 204/340 = 0.6 exactly → 6000 bp.
first = bkt_update_bp(2000, True, RULESET)
assert first == 6000, f"appendix A first-step check failed: {first}"

# --------------------------------------------------------------------------- #
# Invalid-input vectors (identical fallback in both engines)
# --------------------------------------------------------------------------- #
invalid_vectors = [
    {"name": "mastery_out_of_range_high",
     "input": _canonical(_inp(trigger_concept_id="c0001",
                              mastery={"c0001": _m(20000)})),
     "expected": {"reason_code": "STATE_INVALID_FALLBACK"}},
    {"name": "mastery_out_of_range_negative",
     "input": _canonical(_inp(trigger_concept_id="c0001",
                              mastery={"c0001": _m(-5)})),
     "expected": {"reason_code": "STATE_INVALID_FALLBACK"}},
    {"name": "unknown_ruleset_version",
     "input": _canonical(_inp(ruleset_version="0.0.0-not-a-version")),
     "expected": {"reason_code": "STATE_INVALID_FALLBACK"}},
]

# --------------------------------------------------------------------------- #
# Fuzz vectors (engine snapshots; parity between the two engines is the
# point — both must return the same values for identical inputs)
# --------------------------------------------------------------------------- #
rng = random.Random(42)
fuzz_vectors = []
for i in range(120):
    n = rng.randint(0, len(ORDER))
    mastery = {}
    for cid in rng.sample(ORDER, n):
        p = rng.choice([0, 100, 1500, 2000, 3333, 4000, 4001, 5500, 7000,
                        8499, 8500, 9000, 9900])
        attempts = rng.randint(0, 6)
        correct = rng.randint(0, attempts)
        mastery[cid] = _m(p, attempts, correct)
    recent = []
    seq = 1
    target = rng.choice(ORDER + [None])
    for _ in range(rng.randint(0, 6)):
        et = rng.choice(["ANSWER_SUBMITTED", "CONTENT_VIEWED",
                         "DECISION_MADE_LOCAL"])
        cid = rng.choice(ORDER)
        entry = {"seq": seq, "event_type": et, "concept_id": cid,
                 "correct": None, "p_bp_after": None, "last_action": None}
        if et == "ANSWER_SUBMITTED":
            entry["correct"] = rng.random() < 0.5
            entry["p_bp_after"] = rng.choice([1000, 2500, 4100, 4150, 5000,
                                              6100, 8600])
        elif et == "DECISION_MADE_LOCAL":
            entry["last_action"] = rng.choice(["REMEDIATE", "RETRY", "REVISE"])
        recent.append(entry)
        seq += 1
    inp = _inp(
        trigger_event_type=rng.choice(["SESSION_STARTED", "ANSWER_SUBMITTED",
                                       "CONTENT_VIEWED", "DOUBT_ASKED"]),
        trigger_concept_id=target,
        trigger_correct=(rng.choice([True, False])
                         if target else None),
        mastery=mastery,
        recent_events=recent,
        doubt_concept_hint=rng.choice(ORDER + [None]),
        env_network=rng.choice(["online", "weak", "offline", "reconnected"]),
        installed_pack_versions=rng.choice([{PACK: 1}, {}]),
        outbox_nonempty=rng.choice([True, False]),
    )
    out = decide(_to_decision_input(inp), RULESET, REASON_MESSAGES)
    fuzz_vectors.append({
        "name": f"fuzz_{i:03d}",
        "input": _canonical(inp),
        "expected": {
            "action": out.action,
            "target_concept_id": out.target_concept_id,
            "delivery_mode": out.delivery_mode,
            "background_actions": out.background_actions,
            "reason_code": out.reason_code,
            "target_bloom_level": out.target_bloom_level,
            "needs_help": out.needs_help,
        },
    })

# --------------------------------------------------------------------------- #
# Write the fixture
# --------------------------------------------------------------------------- #
fixture = {
    "ruleset_version": RULESET.ruleset_version,
    "bkt_version": RULESET.bkt_version,
    "reason_messages": REASON_MESSAGES,
    "golden": golden_vectors,
    "bkt": bkt_cases,
    "invalid": invalid_vectors,
    "fuzz": fuzz_vectors,
}

out_path = REPO / "tests" / "fixtures" / "rule_vectors.json"
out_path.write_text(json.dumps(fixture, ensure_ascii=False, indent=1),
                    encoding="utf-8")
print(f"wrote {len(golden_vectors)} golden, {len(bkt_cases)} BKT, "
      f"{len(invalid_vectors)} invalid, {len(fuzz_vectors)} fuzz vectors "
      f"to {out_path}")
