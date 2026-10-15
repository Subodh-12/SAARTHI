"""Bayesian Knowledge Tracing (BKT) — pure functions over integer basis points.

Design Document v2 (Section 6, Appendix A) contract:

- Mastery is stored and compared as an INTEGER in basis points (0..10000).
  Python and TypeScript can never disagree through floating-point rounding.
- Update (Appendix A), for a graded answer on a concept with stored mastery
  p = p_bp / 10000 (or ``p_init_bp`` when the concept is new):
      correct:   posterior = p(1 - slip) / (p(1 - slip) + (1 - p) guess)
      wrong:     posterior = p slip / (p slip + (1 - p)(1 - guess))
      p_next     = posterior + (1 - posterior) * learn
  clamped to 0.01..0.99 and stored as basis points ROUNDED HALF UP.
- Every update starts from the stored integer, so replaying the same
  accepted events in canonical order reproduces the same projection exactly.

Exact cross-language parity: the whole update is evaluated in INTEGER
arithmetic (fixed point at 10^4) so Python and JavaScript produce the same
rounded result bit-for-bit. No float ever touches the stored value.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .ruleset import Ruleset

SCALE = 10_000  # basis points per unit probability


def _to_bp_int(x: float) -> int:
    """Convert a rules.json float parameter to fixed-point basis points.

    Both engines use round(x * 10000); for every parameter shipped in
    rules.json this is unambiguous (no .5 boundary at float precision).
    """
    return int(round(float(x) * SCALE))


@dataclass(frozen=True)
class BKTParams:
    p_init_bp: int
    learn_bp: int
    slip_bp: int
    guess_bp: int
    clamp_lo_bp: int
    clamp_hi_bp: int


def bkt_params(ruleset: Ruleset, concept_id: Optional[str] = None) -> BKTParams:
    """Integer BKT parameters from the shared ruleset (per-concept override kept)."""
    b = ruleset.bkt
    overrides = (b.get("per_concept_overrides", {}) or {}).get(concept_id or "", {}) or {}
    clamp = overrides.get("clamp_bp", b.get("clamp_bp", [100, 9900]))
    return BKTParams(
        p_init_bp=int(overrides.get("p_init_bp", b.get("p_init_bp", 2000))),
        learn_bp=_to_bp_int(overrides.get("learn", b.get("learn", 0.15))),
        slip_bp=_to_bp_int(overrides.get("slip", b.get("slip", 0.10))),
        guess_bp=_to_bp_int(overrides.get("guess", b.get("guess", 0.20))),
        clamp_lo_bp=int(clamp[0]),
        clamp_hi_bp=int(clamp[1]),
    )


def clamp_bp(p_bp: int, ruleset: Ruleset, concept_id: Optional[str] = None) -> int:
    params = bkt_params(ruleset, concept_id)
    return max(params.clamp_lo_bp, min(params.clamp_hi_bp, int(p_bp)))


def round_half_up_div(n: int, d: int) -> int:
    """Half-up rounding of the positive integer division n / d.

    Identical formula is implemented in the TypeScript engine:
    q = Math.floor((2*n + d) / (2*d)). Both languages use exact integers
    (max magnitude ~10^12, far below 2^53), so results are identical.
    """
    if d <= 0:
        raise ValueError("denominator must be positive")
    if n < 0:
        # Not used by BKT (all terms non-negative), kept for safety.
        return -((-2 * n + d) // (2 * d))
    return (2 * n + d) // (2 * d)


def bkt_update_bp(p_bp: int, correct: bool, ruleset: Ruleset,
                  concept_id: Optional[str] = None) -> int:
    """Exact Appendix A update from the stored integer mastery.

    Returns the new mastery in basis points (half-up rounded, clamped).
    """
    params = bkt_params(ruleset, concept_id)
    p = max(0, min(SCALE, int(p_bp)))
    S, G, L = params.slip_bp, params.guess_bp, params.learn_bp
    if correct:
        num = p * (SCALE - S)
        den = num + (SCALE - p) * G
    else:
        num = p * S
        den = num + (SCALE - p) * (SCALE - G)
    if den <= 0:
        posterior_num, posterior_den = p, SCALE  # degenerate params: keep prior
    else:
        posterior_num, posterior_den = num, den
    # p_next = posterior + (1 - posterior) * learn, in exact integers:
    #   p_next * SCALE = (posterior_num * SCALE + (posterior_den - posterior_num) * L)
    #                    / posterior_den
    n = posterior_num * SCALE + (posterior_den - posterior_num) * L
    d = posterior_den
    q = round_half_up_div(n, d)
    return max(params.clamp_lo_bp, min(params.clamp_hi_bp, q))


def bkt_update(p_bp: int, correct: bool, ruleset: Ruleset,
               concept_id: Optional[str] = None) -> int:
    """Alias kept for call-site compatibility with the v2 integer contract."""
    return bkt_update_bp(p_bp, correct, ruleset, concept_id)


def mastery_band_bp(p_bp: int, ruleset: Ruleset) -> str:
    """v2 bands: weak below 4000, partial 4000..8499, mastered >= 8500."""
    bands = ruleset.bands
    if p_bp < int(bands.get("weak_below_bp", 4000)):
        return "weak"
    if p_bp < int(bands.get("mastered_at_bp", 8500)):
        return "partial"
    return "mastered"


# --------------------------------------------------------------------------- #
# Event → mastery-effect policy (Design v2 Section 6, "Which events change
# mastery"). Only valid, first-time graded answers update mastery.
# --------------------------------------------------------------------------- #
ANSWER_EVENT = "ANSWER_SUBMITTED"

# Reasons for accepted events that carry no mastery effect (v2 Section 6/8).
EFFECT_MASTERY_UPDATED = "mastery_updated"
EFFECT_NONE = "none"


@dataclass(frozen=True)
class MasteryEffect:
    """Result of applying the mastery transition policy to one event."""
    effect: str                     # EFFECT_MASTERY_UPDATED | EFFECT_NONE
    reason: Optional[str]           # None | REPEAT_SUBMISSION | LEGACY_QUESTION | INVALID_PAYLOAD
    correct: Optional[bool]         # server-regraded result when effect is mastery_updated
    concept_id: Optional[str]
    p_bp_after: Optional[int] = None


def mastery_effect_for_event(
    event: Any,
    ruleset: Ruleset,
    seen_attempt_ids: set[str],
    question_lookup=None,
) -> MasteryEffect:
    """Apply the v2 transition policy to a single learner event.

    question_lookup: callable(question_id, revision) -> object with
    .concept_id and .correct(response) -> bool, or None when the revision
    is unknown/legacy. When None, the payload's own ``correct`` claim is
    trusted only for local decisions (the server always regrades).
    """
    etype = getattr(event.event_type, "value", event.event_type)
    payload = getattr(event, "payload", {}) or {}
    if etype != ANSWER_EVENT:
        return MasteryEffect(EFFECT_NONE, None, None,
                             getattr(event, "concept_id", None))
    attempt_id = str(payload.get("attempt_id") or getattr(event, "event_id", ""))
    if attempt_id in seen_attempt_ids:
        return MasteryEffect(EFFECT_NONE, "REPEAT_SUBMISSION", None,
                             payload.get("concept_id") or getattr(event, "concept_id", None))
    question_id = payload.get("question_id") or getattr(event, "question_id", None)
    revision = payload.get("revision", 1)
    if question_lookup is not None and question_id is not None:
        q = question_lookup(question_id, revision)
        if q is None:
            # Unknown or marked-legacy revision: accepted, no mastery effect.
            return MasteryEffect(EFFECT_NONE, "LEGACY_QUESTION", None,
                                 payload.get("concept_id") or getattr(event, "concept_id", None))
        resp = payload.get("response") if payload.get("response") is not None else payload.get("selected_option")
        correct = bool(q.correct(resp))
        concept_id = q.concept_id
    else:
        correct = bool(payload.get("correct", False))
        concept_id = payload.get("concept_id") or getattr(event, "concept_id", None)
    if not concept_id:
        return MasteryEffect(EFFECT_NONE, "INVALID_PAYLOAD", None, None)
    return MasteryEffect(EFFECT_MASTERY_UPDATED, None, correct, concept_id)


__all__ = [
    "SCALE", "BKTParams", "bkt_params", "bkt_update_bp", "bkt_update",
    "clamp_bp", "round_half_up_div", "mastery_band_bp",
    "ANSWER_EVENT", "EFFECT_MASTERY_UPDATED", "EFFECT_NONE",
    "MasteryEffect", "mastery_effect_for_event",
]
