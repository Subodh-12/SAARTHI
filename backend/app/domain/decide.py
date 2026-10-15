"""Deterministic decision engine v2 — pure functions over explicit inputs.

This is the SHARED RULESET CONTRACT that runs identically in Python (server)
and TypeScript (browser, `frontend/src/engine/decide.ts`). Both load the SAME
`packages/ruleset/rules.json` and must pass the SAME test vectors
(`tests/fixtures/rule_vectors.json`) — Design v2 Sections 6 and 15.

Rules (v2, Decided):
  - The LLM NEVER selects the action. No network, no LLM, no process-local
    memory: this module is a pure deterministic component.
  - Mastery is an INTEGER in basis points (0..10000). Timestamps are never
    inputs. Concept lists are sorted by canonical order / concept ID.
  - First-match action rules with the corrected repeated-attempt guard:
      1. REVISE with alternate content (NO_GAIN_ALT_CONTENT)
      2. REMEDIATE the weakest prerequisite (NO_GAIN_REMEDIATE_PREREQ)
      3. Terminal REVISE with needs_help (INTERVENTIONS_EXHAUSTED)
    The guard NEVER advances a learner whose target is below the mastered
    threshold just to escape a loop.
  - Every output contains exactly one learning action, a feasible delivery
    mode, zero or more sorted background actions, a stable reason code, the
    ruleset version and the needs_help flag.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .bkt import SCALE, mastery_band_bp
from .ruleset import Ruleset, UnknownRulesetError


# --------------------------------------------------------------------------- #
# Input / output shapes (data-only; identical in TypeScript)
# --------------------------------------------------------------------------- #
@dataclass
class MasteryEntry:
    p_bp: int
    attempts: int = 0
    correct: int = 0
    last_event_seq: int = 0


@dataclass
class RecentEvent:
    """Minimal deterministic projection of a past event (oldest → newest)."""
    seq: int
    event_type: str
    concept_id: Optional[str] = None
    correct: Optional[bool] = None          # graded answers only
    p_bp_after: Optional[int] = None        # mastery (bp) after a graded answer
    last_action: Optional[str] = None       # decision that followed, e.g. REVISE


@dataclass
class DecisionInput:
    trigger_event_type: str
    trigger_concept_id: Optional[str]       # concept of the last graded answer
    trigger_correct: Optional[bool]         # last graded answer result (None = not graded)
    mastery: dict[str, MasteryEntry]
    recent_events: list[RecentEvent]
    prereqs: dict[str, list[str]]
    concept_order: list[str]
    chapter_id_for_concept: dict[str, str] = field(default_factory=dict)
    doubt_concept_hint: Optional[str] = None
    env_network: str = "online"             # online | weak | offline | reconnected
    installed_pack_versions: dict[str, int] = field(default_factory=dict)
    required_pack_for_concept: dict[str, str] = field(default_factory=dict)
    storage_free_mb: int = 1_000_000
    battery_saver: bool = False
    outbox_nonempty: bool = False
    ruleset_version: str = "1.0.0"
    bloom_mastery: dict[str, dict[str, MasteryEntry]] = field(default_factory=dict)
    available_bloom_levels_for_concept: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class DecisionOutput:
    action: str                              # REMEDIATE | RETRY | REVISE | ADVANCE
    target_concept_id: str
    delivery_mode: str                       # cached | rich | prefetch_then_offline
    background_actions: list[str]            # sorted subset of {SYNC, PREFETCH}
    reason_code: str
    target_bloom_level: Optional[str] = None
    needs_help: bool = False
    rule_index: int = -1
    fallback: bool = False


# --------------------------------------------------------------------------- #
# Typed engine error + state validation (v2: "unknown ruleset version gives a
# typed error and the fallback decision")
# --------------------------------------------------------------------------- #
def engine_error(inp: DecisionInput, ruleset: Ruleset) -> Optional[str]:
    """Return a typed error code when the input state cannot be trusted.

    Returns None when the state is valid. The caller logs the error at high
    severity; `decide` still returns the safe fallback decision.
    """
    if inp.ruleset_version != ruleset.ruleset_version:
        return "RULESET_UNKNOWN"
    for cid, m in inp.mastery.items():
        if not isinstance(m.p_bp, int) or m.p_bp < 0 or m.p_bp > SCALE:
            return "STATE_INVALID"
    if inp.trigger_correct is not None and inp.trigger_concept_id is None:
        return "STATE_INVALID"
    return None


def state_is_valid(inp: DecisionInput, ruleset: Ruleset) -> bool:
    return engine_error(inp, ruleset) is None


# --------------------------------------------------------------------------- #
# Reason-code → Odia strings (developer fallbacks; i18n dict overrides)
# --------------------------------------------------------------------------- #
DEFAULT_REASON_OR = {
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


def _reason_or(reason_code: str, reason_messages: dict[str, str]) -> str:
    if reason_messages.get(reason_code):
        return reason_messages[reason_code]
    return DEFAULT_REASON_OR.get(reason_code, "ଆଗାମୀ କାମ ଜାରି ରଖ।")


# --------------------------------------------------------------------------- #
# Deterministic helpers
# --------------------------------------------------------------------------- #
def _weakest_prereq(concept_id: str, inp: DecisionInput) -> Optional[str]:
    """Weakest prerequisite of concept_id: lowest p_bp, ties by concept ID."""
    best: Optional[tuple[int, str]] = None
    for pre in inp.prereqs.get(concept_id, []) or []:
        p = inp.mastery[pre].p_bp if pre in inp.mastery else 0
        key = (p, pre)
        if best is None or key < best:
            best = key
    return best[1] if best else None


def _prereqs_mastered(concept_id: str, inp: DecisionInput, ruleset: Ruleset) -> bool:
    mastered_at = int(ruleset.bands.get("mastered_at_bp", 8500))
    return all(
        inp.mastery.get(pre, MasteryEntry(0)).p_bp >= mastered_at
        for pre in inp.prereqs.get(concept_id, []) or []
    )


def _first_concept_without_prereqs(inp: DecisionInput) -> Optional[str]:
    for cid in inp.concept_order:
        if not (inp.prereqs.get(cid) or []):
            return cid
    return None


def _next_eligible_concept(inp: DecisionInput, ruleset: Ruleset,
                           after_concept: Optional[str] = None) -> Optional[str]:
    """First concept in chapter order that is not mastered and whose
    prerequisites are all at or above the mastered threshold (v2)."""
    mastered_at = int(ruleset.bands.get("mastered_at_bp", 8500))
    started = after_concept is None
    for cid in inp.concept_order:
        if not started:
            if cid == after_concept:
                started = True
            continue
        if inp.mastery.get(cid, MasteryEntry(0)).p_bp >= mastered_at:
            continue
        if _prereqs_mastered(cid, inp, ruleset):
            return cid
    return None


def _lowest_mastery_with_mastered_prereqs(inp: DecisionInput,
                                          ruleset: Ruleset) -> Optional[str]:
    """Lowest-mastery concept among those whose prereqs are all mastered;
    ties by chapter order then concept ID (deterministic)."""
    best: Optional[tuple[int, int, str]] = None
    for idx, cid in enumerate(inp.concept_order):
        if not _prereqs_mastered(cid, inp, ruleset):
            continue
        m = inp.mastery.get(cid)
        p = m.p_bp if m else 0
        key = (p, idx, cid)
        if best is None or key < best:
            best = key
    return best[2] if best else None


def _graph_distance(from_cid: str, to_cid: str, inp: DecisionInput, max_depth: int = 6) -> int:
    """BFS distance over the prerequisite graph (undirected), capped."""
    if from_cid == to_cid:
        return 0
    # Undirected adjacency: prereqs + reverse edges
    adj: dict[str, set[str]] = {}
    for cid, pres in (inp.prereqs or {}).items():
        for pre in pres or []:
            adj.setdefault(cid, set()).add(pre)
            adj.setdefault(pre, set()).add(cid)
    frontier = {from_cid}
    seen = {from_cid}
    for depth in range(1, max_depth + 1):
        nxt: set[str] = set()
        for node in frontier:
            for nb in adj.get(node, ()):  # deterministic set iteration order does not
                if nb in seen:            # affect the *distance* value
                    continue
                if nb == to_cid:
                    return depth
                seen.add(nb)
                nxt.add(nb)
        frontier = nxt
        if not frontier:
            break
    return max_depth + 1


def _nearest_installed_concept(inp: DecisionInput, ruleset: Ruleset) -> Optional[str]:
    """Nearest concept whose pack IS installed, by graph distance from the
    target, ties by chapter order (v2: CONTENT_NOT_AVAILABLE_OFFLINE)."""
    target = inp.trigger_concept_id or _select_target_concept(inp, ruleset)[0]
    if not target:
        return None
    best: Optional[tuple[int, int, str]] = None
    for idx, cid in enumerate(inp.concept_order):
        pack_id = inp.required_pack_for_concept.get(cid)
        if not pack_id or pack_id in inp.installed_pack_versions:
            dist = _graph_distance(target, cid, inp)
            key = (dist, idx, cid)
            if best is None or key < best:
                best = key
    return best[2] if best else None


def _target_pack_installed(cid: str, inp: DecisionInput) -> bool:
    pack_id = inp.required_pack_for_concept.get(cid)
    if not pack_id:
        return True
    return pack_id in inp.installed_pack_versions


# --------------------------------------------------------------------------- #
# Target-concept selection (v2 Section 6)
# --------------------------------------------------------------------------- #
def _select_target_concept(inp: DecisionInput,
                           ruleset: Ruleset) -> tuple[str, str]:
    """Return (target_concept_id, reason_code_used_for_selection).

    The target is the concept of the last graded answer or, failing that,
    the doubt's concept hint; otherwise the concept with the lowest mastery
    among those whose prerequisites are all mastered, ties by chapter order.
    """
    if inp.trigger_concept_id and inp.trigger_concept_id in inp.concept_order:
        return inp.trigger_concept_id, "last_graded"
    if inp.doubt_concept_hint and inp.doubt_concept_hint in inp.concept_order:
        return inp.doubt_concept_hint, "doubt_hint"
    cid = _lowest_mastery_with_mastered_prereqs(inp, ruleset)
    return (cid or ""), "lowest_mastery"


# --------------------------------------------------------------------------- #
# Repeated-attempt guard (v2 Section 6, corrected)
# --------------------------------------------------------------------------- #
def _graded_on_target(inp: DecisionInput, target: str) -> list[RecentEvent]:
    return [e for e in inp.recent_events
            if e.event_type == "ANSWER_SUBMITTED" and e.concept_id == target
            and e.p_bp_after is not None]


def guard_state(inp: DecisionInput, target: str, ruleset: Ruleset) -> tuple[int, bool]:
    """Return (attempts_without_gain, alt_content_shown).

    attempts_without_gain: graded answers on the target since its mastery
    last rose by at least min_gain_bp. alt_content_shown: an alternate
    content REVISE for the target within the current guard cycle.
    """
    min_gain = int(ruleset.guard.get("min_gain_bp",
                                     ruleset.repetition_guard.get("min_gain_bp", 200)))
    graded = _graded_on_target(inp, target)
    # Find the last index k where mastery rose by >= min_gain between
    # graded[k-1] and graded[k]; the cycle starts at k.
    cycle_start = 0
    for k in range(1, len(graded)):
        if (graded[k].p_bp_after or 0) - (graded[k - 1].p_bp_after or 0) >= min_gain:
            cycle_start = k
    attempts_without_gain = max(0, len(graded) - cycle_start)
    cycle_start_seq = graded[cycle_start].seq if graded else 0
    alt = any(
        e.concept_id == target and e.last_action == "REVISE"
        and e.seq >= cycle_start_seq
        for e in inp.recent_events
    )
    return attempts_without_gain, alt


# --------------------------------------------------------------------------- #
# Delivery mode + background actions (v2 Sections 6 and 10)
# --------------------------------------------------------------------------- #
def select_delivery_mode(inp: DecisionInput, ruleset: Ruleset,
                         target: str) -> str:
    network = inp.env_network
    if network in ("offline",):
        return "cached"
    if _target_pack_installed(target, inp):
        return ruleset.delivery.get(network, "cached")
    # Target pack missing: prefetch_then_offline only on a good network.
    if network in ("online", "reconnected"):
        return "prefetch_then_offline"
    return "cached"


def select_background_actions(inp: DecisionInput, ruleset: Ruleset,
                              target: str, reason_code: str = "") -> list[str]:
    network = inp.env_network
    actions: list[str] = []
    if network != "offline" and inp.outbox_nonempty:
        actions.append("SYNC")
    prefetch_ok = (
        (
            (network in ("online", "reconnected") and not _target_pack_installed(target, inp))
            or (reason_code == "CONTENT_NOT_AVAILABLE_OFFLINE")
        )
        and not inp.battery_saver
        and inp.storage_free_mb >= int(ruleset.prefetch.get("min_free_mb", 150))
    )
    if prefetch_ok:
        actions.append("PREFETCH")
    return sorted(set(actions), key=lambda a: ["PREFETCH", "SYNC"].index(a))


CANONICAL_BLOOM_LEVELS = [
    "remember", "understand", "apply", "analyze", "evaluate", "create",
]


def select_target_bloom_level(
    action: str,
    target_concept_id: str,
    reason_code: str,
    inp: DecisionInput,
    ruleset: Ruleset,
) -> Optional[str]:
    """Select the target Bloom's Taxonomy cognitive level deterministically."""
    if not target_concept_id:
        return None

    bloom_cfg = getattr(ruleset, "bloom", None) or {}
    levels_all = bloom_cfg.get("levels") or CANONICAL_BLOOM_LEVELS
    foundational = bloom_cfg.get("foundational_levels") or ["remember", "understand"]
    higher_order = bloom_cfg.get("higher_order_levels") or ["apply", "analyze", "evaluate", "create"]
    proficient_at_bp = int(bloom_cfg.get("proficient_at_bp", 7000))
    mastered_at_bp = int(bloom_cfg.get("mastered_at_bp", 8500))

    concept_avail = (inp.available_bloom_levels_for_concept or {}).get(target_concept_id)
    if concept_avail:
        avail_levels = [lvl for lvl in levels_all if lvl in concept_avail]
        if not avail_levels:
            avail_levels = list(concept_avail)
    else:
        avail_levels = list(levels_all)

    if not avail_levels:
        avail_levels = ["remember"]

    concept_bloom_m = (inp.bloom_mastery or {}).get(target_concept_id, {})

    def get_level_bp(lvl: str) -> int:
        if lvl in concept_bloom_m:
            return concept_bloom_m[lvl].p_bp
        if lvl == "remember" and target_concept_id in inp.mastery:
            return inp.mastery[target_concept_id].p_bp
        bkt_cfg = getattr(ruleset, "bkt", None) or {}
        return int(bkt_cfg.get("p_init_bp", 2000))

    chosen: str
    if action == "ADVANCE":
        chosen = avail_levels[0]

    elif action == "REMEDIATE":
        cand = [lvl for lvl in avail_levels if lvl in foundational]
        if not cand:
            cand = avail_levels
        below = [lvl for lvl in cand if get_level_bp(lvl) < proficient_at_bp]
        chosen = below[0] if below else cand[0]

    elif action == "REVISE":
        if reason_code == "SLICE_COMPLETE":
            ho_cand = [lvl for lvl in avail_levels if lvl in higher_order]
            chosen = ho_cand[-1] if ho_cand else avail_levels[-1]
        else:
            cand = [lvl for lvl in avail_levels if lvl in foundational]
            chosen = cand[0] if cand else avail_levels[0]

    elif action == "RETRY":
        first_unproficient: Optional[str] = None
        for lvl in levels_all:
            if get_level_bp(lvl) < proficient_at_bp:
                first_unproficient = lvl
                break

        if first_unproficient is not None:
            desired = first_unproficient
        else:
            first_unmastered: Optional[str] = None
            for lvl in levels_all:
                if get_level_bp(lvl) < mastered_at_bp:
                    first_unmastered = lvl
                    break
            desired = first_unmastered or levels_all[-1]

        if desired in avail_levels:
            chosen = desired
        else:
            desired_idx = levels_all.index(desired) if desired in levels_all else len(levels_all) - 1
            lower_avail = [
                lvl for lvl in avail_levels
                if (levels_all.index(lvl) if lvl in levels_all else 0) <= desired_idx
            ]
            chosen = lower_avail[-1] if lower_avail else avail_levels[-1]

    else:
        chosen = avail_levels[0]

    if chosen not in avail_levels:
        chosen = avail_levels[0]
    return chosen


# --------------------------------------------------------------------------- #
# Trajectory check (v2 Section 6: validated before save/display)
# --------------------------------------------------------------------------- #
VALID_ACTIONS = ("REMEDIATE", "RETRY", "REVISE", "ADVANCE")
VALID_DELIVERY = ("cached", "rich", "prefetch_then_offline")
VALID_BACKGROUND = ("SYNC", "PREFETCH")


def trajectory_check(out: DecisionOutput, inp: DecisionInput,
                     ruleset: Ruleset) -> bool:
    if out.target_concept_id and out.target_concept_id not in inp.concept_order:
        return False
    if out.action not in VALID_ACTIONS:
        return False
    if out.reason_code not in DEFAULT_REASON_OR:
        return False
    if out.delivery_mode not in VALID_DELIVERY:
        return False
    if out.delivery_mode == "rich" and inp.env_network == "offline":
        return False
    if any(a not in VALID_BACKGROUND for a in out.background_actions):
        return False
    if out.background_actions != sorted(
            out.background_actions, key=lambda a: ["PREFETCH", "SYNC"].index(a)):
        return False
    if out.target_bloom_level is not None and out.target_bloom_level not in CANONICAL_BLOOM_LEVELS:
        return False
    if inp.ruleset_version != ruleset.ruleset_version:
        return False
    return True


# --------------------------------------------------------------------------- #
# Top-level decide()
# --------------------------------------------------------------------------- #
def decide(inp: DecisionInput, ruleset: Ruleset,
           reason_messages: Optional[dict[str, str]] = None) -> DecisionOutput:
    rm = reason_messages or {}
    weak_below = int(ruleset.bands.get("weak_below_bp", 4000))
    mastered_at = int(ruleset.bands.get("mastered_at_bp", 8500))
    guard_cfg = ruleset.guard or ruleset.repetition_guard
    attempts_allowed = int(guard_cfg.get("attempts_without_gain", 3))

    # --- Rule 0: invalid state or unknown ruleset → safe fallback decision.
    err = engine_error(inp, ruleset)
    if err is not None:
        target = (inp.trigger_concept_id
                  if inp.trigger_concept_id in inp.concept_order else "")
        if not target:
            first = _first_concept_without_prereqs(inp) or (inp.concept_order[0] if inp.concept_order else "")
            if first:
                out = DecisionOutput(
                    action="ADVANCE", target_concept_id=first,
                    delivery_mode=select_delivery_mode(inp, ruleset, first),
                    background_actions=select_background_actions(inp, ruleset, first),
                    reason_code="STATE_INVALID_FALLBACK",
                    target_bloom_level="remember",
                    needs_help=False,
                    rule_index=0, fallback=True,
                )
                return out
            # No concepts at all: nothing sensible to point at.
            return DecisionOutput(
                action="RETRY", target_concept_id="",
                delivery_mode="cached", background_actions=[],
                reason_code="STATE_INVALID_FALLBACK",
                target_bloom_level=None,
                needs_help=False,
                rule_index=0, fallback=True,
            )
        return DecisionOutput(
            action="RETRY", target_concept_id=target,
            delivery_mode=select_delivery_mode(inp, ruleset, target),
            background_actions=select_background_actions(inp, ruleset, target),
            reason_code="STATE_INVALID_FALLBACK",
            target_bloom_level="remember",
            needs_help=False,
            rule_index=0, fallback=True,
        )

    # --- Rule 1: cold start (no mastery rows at all).
    if not inp.mastery:
        first = _first_concept_without_prereqs(inp)
        if first is not None:
            return _finish(inp, ruleset, rm, "ADVANCE", first,
                           "COLD_START", rule_index=1)
        # Every concept has prerequisites: remediate the weakest unmet one.
        weakest = _most_blocked_prereq(inp)
        if weakest is not None:
            return _finish(inp, ruleset, rm, "REMEDIATE", weakest,
                           "BLOCKED_BY_PREREQ", rule_index=1)
        return _finish(inp, ruleset, rm, "RETRY", "",
                       "STATE_INVALID_FALLBACK", rule_index=1, fallback=True)

    # --- Target selection.
    target, _why = _select_target_concept(inp, ruleset)
    if not target:
        return _finish(inp, ruleset, rm, "RETRY", "",
                       "STATE_INVALID_FALLBACK", rule_index=0, fallback=True)
    m = inp.mastery.get(target)
    if m is None or (m.attempts == 0 and inp.trigger_correct is None):
        # Target has never been attempted: advance if prereqs are mastered, else remediate prereq gap
        if _prereqs_mastered(target, inp, ruleset):
            return _finish(inp, ruleset, rm, "ADVANCE", target,
                           "MASTERED_ADVANCE", rule_index=7)
        else:
            weakest = _weakest_prereq(target, inp) or _most_blocked_prereq(inp)
            if weakest:
                return _finish(inp, ruleset, rm, "REMEDIATE", weakest,
                               "BLOCKED_BY_PREREQ", rule_index=7)
    p = m.p_bp if m is not None else int(ruleset.bkt.get("p_init_bp", 2000))

    # --- Rule 2: repeated-attempt guard (3+ graded answers on T without a
    # gain of at least min_gain_bp).
    attempts_without_gain, alt_shown = guard_state(inp, target, ruleset)
    if attempts_without_gain >= attempts_allowed:
        if not alt_shown:
            return _finish(inp, ruleset, rm, "REVISE", target,
                           "NO_GAIN_ALT_CONTENT", rule_index=2)
        weakest = _weakest_prereq(target, inp)
        if weakest is not None:
            pre_p = inp.mastery.get(weakest, MasteryEntry(0)).p_bp
            if pre_p < mastered_at:
                return _finish(inp, ruleset, rm, "REMEDIATE", weakest,
                               "NO_GAIN_REMEDIATE_PREREQ", rule_index=2)
        # Terminal: interventions exhausted. The learner is never advanced
        # while T is below mastered.
        return _finish(inp, ruleset, rm, "REVISE", target,
                       "INTERVENTIONS_EXHAUSTED", needs_help=True, rule_index=2)

    # --- Rules 3-4: weak concept / weak prerequisite.
    if p < weak_below:
        weakest = _weakest_prereq(target, inp)
        if weakest is not None:
            pre_p = inp.mastery.get(weakest, MasteryEntry(0)).p_bp
            if pre_p < weak_below:
                return _finish(inp, ruleset, rm, "REMEDIATE", weakest,
                               "WEAK_PREREQ_GAP", rule_index=3)
        return _finish(inp, ruleset, rm, "REMEDIATE", target,
                       "WEAK_CONCEPT", rule_index=4)

    # --- Rules 5-6: partial mastery, retry.
    if p < mastered_at:
        last_correct = inp.trigger_correct
        if last_correct is None and inp.recent_events:
            for e in reversed(inp.recent_events):
                if e.event_type == "ANSWER_SUBMITTED" and e.correct is not None:
                    last_correct = e.correct
                    break
        if last_correct is False:
            return _finish(inp, ruleset, rm, "RETRY", target,
                           "WRONG_RETRY", rule_index=5)
        return _finish(inp, ruleset, rm, "RETRY", target,
                       "PARTIAL_PRACTICE", rule_index=6)

    # --- Rule 7: mastered → advance to the next eligible concept.
    nxt = _next_eligible_concept(inp, ruleset, after_concept=target)
    if nxt is not None:
        return _finish(inp, ruleset, rm, "ADVANCE", nxt,
                       "MASTERED_ADVANCE", rule_index=7)
    # No eligible concept: slice complete (everything mastered) or blocked.
    all_mastered = all(
        inp.mastery.get(cid, MasteryEntry(0)).p_bp >= mastered_at
        for cid in inp.concept_order
    )
    if all_mastered:
        oldest = min(
            inp.concept_order,
            key=lambda cid: (inp.mastery.get(cid, MasteryEntry(0)).last_event_seq, cid),
        )
        return _finish(inp, ruleset, rm, "REVISE", oldest,
                       "SLICE_COMPLETE", rule_index=7)
    weakest_unmet = _most_blocked_prereq(inp)
    if weakest_unmet is not None:
        return _finish(inp, ruleset, rm, "REMEDIATE", weakest_unmet,
                       "BLOCKED_BY_PREREQ", rule_index=7)
    return _finish(inp, ruleset, rm, "RETRY", target,
                   "STATE_INVALID_FALLBACK", rule_index=7, fallback=True)


def _most_blocked_prereq(inp: DecisionInput) -> Optional[str]:
    """The weakest prerequisite that blocks any concept (lowest mastery)."""
    blocked: set[str] = set()
    for cid, pres in (inp.prereqs or {}).items():
        blocked.update(pres or [])
    best: Optional[tuple[int, str]] = None
    for cid in blocked:
        p = inp.mastery.get(cid, MasteryEntry(0)).p_bp
        key = (p, cid)
        if best is None or key < best:
            best = key
    return best[1] if best else None


def _finish(inp: DecisionInput, ruleset: Ruleset, rm: dict[str, str],
            action: str, target: str, reason_code: str,
            needs_help: bool = False, rule_index: int = -1,
            fallback: bool = False) -> DecisionOutput:
    """Assemble the output, applying the offline-missing-pack substitution
    (CONTENT_NOT_AVAILABLE_OFFLINE) and the trajectory check."""
    out_target = target
    reason = reason_code
    if out_target and not _target_pack_installed(out_target, inp) \
            and inp.env_network == "offline":
        nearest = _nearest_installed_concept(inp, ruleset)
        if nearest is not None and nearest != out_target:
            out_target = nearest
            reason = "CONTENT_NOT_AVAILABLE_OFFLINE"
        else:
            # No pack installed at all (v2: storage corruption removed the
            # seed pack): the fallback decision is returned and the UI asks
            # the learner to reconnect and download.
            return DecisionOutput(
                action="RETRY", target_concept_id=out_target,
                delivery_mode="cached", background_actions=[],
                reason_code="STATE_INVALID_FALLBACK",
                target_bloom_level="remember" if out_target else None,
                needs_help=False,
                rule_index=0, fallback=True,
            )
    target_bloom = select_target_bloom_level(action, out_target, reason, inp, ruleset)
    out = DecisionOutput(
        action=action, target_concept_id=out_target,
        delivery_mode=select_delivery_mode(inp, ruleset, out_target),
        background_actions=select_background_actions(inp, ruleset, out_target, reason),
        reason_code=reason,
        target_bloom_level=target_bloom,
        needs_help=needs_help,
        rule_index=rule_index, fallback=fallback,
    )
    if not trajectory_check(out, inp, ruleset):
        # Fallback decision (v2): reason STATE_INVALID_FALLBACK, logged by caller.
        # RETRY on the last concept, or on the first concept when no graded
        # concept exists. With NO concepts at all, RETRY with an empty target
        # is the only safe output (there is nothing to advance to).
        tgt = (inp.trigger_concept_id
               if inp.trigger_concept_id in inp.concept_order else
               (inp.concept_order[0] if inp.concept_order else ""))
        return DecisionOutput(
            action="RETRY",
            target_concept_id=tgt,
            delivery_mode="cached",
            background_actions=[],
            reason_code="STATE_INVALID_FALLBACK",
            target_bloom_level="remember" if tgt else None,
            needs_help=False,
            rule_index=0, fallback=True,
        )
    return out


__all__ = [
    "MasteryEntry", "RecentEvent", "DecisionInput", "DecisionOutput",
    "decide", "engine_error", "state_is_valid", "trajectory_check",
    "select_delivery_mode", "select_background_actions",
    "guard_state", "mastery_band_bp",
    "CANONICAL_BLOOM_LEVELS", "select_target_bloom_level",
]
