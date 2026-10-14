"""Verification gate for candidate misconceptions — pure, deterministic.

A candidate cause (from diagnose.py) is NOT accepted on one answer. It becomes
"verified" only with additional, independent, teacher-mapped evidence:

  verified   — ≥2 distinct questions answered incorrectly, both mapped to the
               same tag, and no correct answer on any tag-mapped question
               (a correct follow-up refutes the candidate).
  candidate  — exactly one mapped incorrect answer; more evidence required.
  refuted    — the learner answered a tag-mapped question correctly.
  insufficient_evidence — incorrect answers exist but none is mapped to a
               teacher-authored tag.
  none       — no relevant evidence.

Unanswered events never contribute evidence (they carry evidence="none").
Deriving status from the event history keeps this idempotent: duplicate or
retried events are collapsed by question_id, so no answer can be counted twice.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

VERIFICATION_STATUSES = ("none", "candidate", "verified", "refuted",
                         "insufficient_evidence")


@dataclass
class TagEvidence:
    question_id: str
    tag: str                       # teacher-authored tag; "" when unmapped
    evidence: str                  # "correct" | "incorrect" | "partial" | "none"


def verification_status(evidences: Iterable[TagEvidence]) -> str:
    """Collapse evidence (deduped by (question_id, tag)) into a status."""
    by_question: dict[tuple[str, str], TagEvidence] = {}
    for ev in evidences:
        by_question[(ev.question_id, ev.tag)] = ev  # retries don't double-count

    incorrect_by_tag: dict[str, set[str]] = {}
    correct_tags: set[str] = set()
    any_incorrect = False
    for ev in by_question.values():
        if ev.evidence == "none":
            continue  # unanswered is never evidence of anything
        if ev.evidence == "correct":
            if ev.tag:
                correct_tags.add(ev.tag)
            continue
        any_incorrect = True
        if ev.tag:
            incorrect_by_tag.setdefault(ev.tag, set()).add(ev.question_id)

    if correct_tags & set(incorrect_by_tag):
        return "refuted"
    for tag, qids in incorrect_by_tag.items():
        if len(qids) >= 2:
            return "verified"
    if incorrect_by_tag:
        return "candidate"
    if any_incorrect:
        return "insufficient_evidence"
    return "none"


__all__ = ["TagEvidence", "VERIFICATION_STATUSES", "verification_status"]
