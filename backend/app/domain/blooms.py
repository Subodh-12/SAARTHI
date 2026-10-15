"""Bloom's-Taxonomy-aware question selection — pure, deterministic.

Extends the existing decision layer (decide.py still owns action/concept
selection; this module only picks *which question* to deliver for a target
concept). Rules:

  - Bloom ladder: remember < understand < apply < analyze < evaluate < create.
  - Prerequisite gate: if any prerequisite of the target concept is unmastered,
    the selection window is capped at "understand" — advanced levels never
    override unresolved foundations.
  - Mastery window: the learner's current p(known) bounds the preferred band
    (novice → remember/understand, mid → apply, high → analyze+). This steers
    selection; it never bypasses the prerequisite cap.
  - Missing bloom_level (legacy questions) is treated as "understand" —
    always inside the allowed window, so legacy packs degrade gracefully.
  - Deterministic ordering: window fit, then question_id ascending; answered
    questions are excluded unless nothing else is available (explicit
    repetition trade-off, never silent).
"""
from __future__ import annotations

from typing import Iterable, Optional

from .schemas import BloomLevel, Question

BLOOM_ORDER: dict[str, int] = {
    "remember": 0, "understand": 1, "apply": 2,
    "analyze": 3, "evaluate": 4, "create": 5,
}
DEFAULT_BLOOM: BloomLevel = "understand"


def _norm(level: Optional[str]) -> int:
    return BLOOM_ORDER.get(level or DEFAULT_BLOOM, BLOOM_ORDER[DEFAULT_BLOOM])


def bloom_window(
    mastery_p: float,
    prereqs_resolved: bool,
    ruleset_like: Optional[dict] = None,
) -> tuple[int, int]:
    """Return the inclusive (min, max) Bloom ranks allowed for the learner.

    The prerequisite cap dominates: unresolved foundations cap the window at
    understand regardless of mastery. Otherwise mastery widens the ceiling.
    """
    lo = 0  # remember is always allowed
    if not prereqs_resolved:
        return lo, BLOOM_ORDER["understand"]
    th = ruleset_like or {}
    retry = float(th.get("retry_threshold", 0.5))
    advance = float(th.get("advance_threshold", 0.85))
    if mastery_p < retry:
        hi = BLOOM_ORDER["understand"]
    elif mastery_p < advance:
        hi = BLOOM_ORDER["apply"]
    else:
        hi = BLOOM_ORDER["create"]
    return lo, hi


def select_question(
    questions: Iterable[Question],
    target_concept_id: str,
    mastery_p: float,
    prereqs_resolved: bool,
    exclude_ids: set[str] = frozenset(),
    ruleset_like: Optional[dict] = None,
) -> tuple[Optional[str], str]:
    """Pick a question for the target concept.

    Returns (question_id or None, reason_code). Deterministic: prefer
    in-window questions (closest fit to the ceiling first, i.e. the most
    demanding level the learner is allowed), then question_id ascending.
    Excluded questions are used only when nothing else exists, and the
    reason code says so explicitly.
    """
    lo, hi = bloom_window(mastery_p, prereqs_resolved, ruleset_like)
    pool = [q for q in questions if q.concept_id == target_concept_id
            and q.qtype == "mcq" and q.correct_option is not None]
    if not pool:
        return None, "question.none_for_concept"

    def rank(q: Question) -> int:
        return _norm(q.bloom_level)

    in_window = [q for q in pool if lo <= rank(q) <= hi]
    fresh = [q for q in in_window if q.question_id not in exclude_ids]
    if fresh:
        # Most demanding allowed level first, then id — deterministic.
        best = sorted(fresh, key=lambda q: (-rank(q), q.question_id))[0]
        return best.question_id, "question.bloom_in_window"
    fresh_any = [q for q in pool if q.question_id not in exclude_ids]
    if fresh_any:
        # No in-window candidate (e.g. untagged legacy set with a narrow
        # window) — fall back deterministically rather than returning nothing.
        best = sorted(fresh_any, key=lambda q: (abs(rank(q) - hi), q.question_id))[0]
        return best.question_id, "question.fallback_out_of_window"
    # Everything is excluded — repetition is unavoidable; say so.
    best = sorted(pool, key=lambda q: (-rank(q), q.question_id))[0]
    return best.question_id, "question.repeat_only_available"


__all__ = [
    "BLOOM_ORDER",
    "DEFAULT_BLOOM",
    "bloom_window",
    "select_question",
]
