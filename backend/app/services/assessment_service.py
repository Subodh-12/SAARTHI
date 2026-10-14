"""Assessment service — MCQ + short-answer, integer BKT mastery update.

The server regrades every graded answer from its OWN answer key; the
client's correct_claim is never trusted for mastery (v2 Section 6).
Mastery is stored as integer basis points; every update starts from the
persisted integer, so replay is exact.
"""
from __future__ import annotations

import time
from typing import Optional

from ..content.pack_loader import PackContentIndex
from ..domain.assess import evaluate_submission, evaluate_short_answer
from ..domain.bkt import bkt_update_bp, mastery_band_bp
from ..domain.ruleset import get_ruleset
from ..domain.schemas import (
    AssessmentResult, AssessmentSubmission, EvidenceType, EventType,
    MasteryRecord, Outcome, new_event_id,
)
from ..repositories import EventRepository, MasteryRepository


class AssessmentService:
    def __init__(self, pack: PackContentIndex, events: EventRepository,
                 mastery: MasteryRepository) -> None:
        self.pack = pack
        self.events = events
        self.mastery = mastery

    async def submit_assessment(
        self, learner_id: str, device_id: str, sub: AssessmentSubmission,
        seq: int,
    ) -> AssessmentResult:
        """Evaluate (server-side regrade), persist the event atomically,
        update mastery in basis points, return the result."""
        question = self.pack.get_question(sub.question_id)
        if not question:
            raise ValueError(f"unknown question: {sub.question_id}")
        if question.qtype == "mcq":
            correct, evidence = evaluate_submission(question, sub)
        else:
            correct, evidence = evaluate_short_answer(question, sub)
        ruleset = get_ruleset()
        ts = int(time.time() * 1000)
        attempt_id = sub.attempt_id or new_event_id()
        event_id = new_event_id()
        event = _event(
            event_id=event_id, device_id=device_id, learner_id=learner_id,
            seq=seq, client_ts=sub.submitted_at or ts,
            event_type=EventType.ANSWER_SUBMITTED,
            concept_id=question.concept_id, chapter_id=question.chapter_id,
            question_id=question.question_id,
            payload={
                "attempt_id": attempt_id,
                "question_id": question.question_id,
                "revision": getattr(question, "revision", 1),
                "response": (sub.selected_option if question.qtype == "mcq"
                             else sub.answer_text),
                "correct": correct,           # server-regraded result
                "correct_claim": sub.correct_claim,  # client claim (audit only)
                "selected_option": sub.selected_option,
                "answer_text": sub.answer_text,
                "duration_ms": sub.duration_ms,
                "last_action": "ASSESS",
            },
        )
        # Insert event (idempotent by (device_id, seq))
        result = await self.events.insert_event(event)
        # Update mastery only on first-time acceptance, never on duplicates.
        if result.outcome == Outcome.ACCEPTED:
            existing = await self.mastery.get_mastery(learner_id)
            m = next((r for r in existing if r.concept_id == question.concept_id), None)
            p_prior = m.p_bp if m else int(ruleset.bkt.get("p_init_bp", 2000))
            p_new = bkt_update_bp(p_prior, bool(correct), ruleset, question.concept_id)
            band = mastery_band_bp(p_new, ruleset)
            attempts = (m.attempts if m else 0) + 1
            correct_n = (m.correct if m else 0) + (1 if correct else 0)
            await self.mastery.upsert_mastery(
                learner_id=learner_id, concept_id=question.concept_id,
                p_bp=p_new, band=band, attempts=attempts,
                correct=correct_n, last_event_seq=seq,
                bkt_version=ruleset.bkt_version,
            )
            m_after = MasteryRecord(
                concept_id=question.concept_id, p_bp=p_new, band=band,
                attempts=attempts, correct=correct_n, last_event_seq=seq,
            )
        else:
            existing = await self.mastery.get_mastery(learner_id)
            m_after = next((r for r in existing if r.concept_id == question.concept_id),
                           MasteryRecord(concept_id=question.concept_id,
                                         p_bp=int(ruleset.bkt.get("p_init_bp", 2000)),
                                         band="weak", attempts=0, correct=0))
        return AssessmentResult(
            question_id=question.question_id, attempt_id=attempt_id,
            correct=correct, evidence=evidence,
            explanation_or=question.explanation_or,
            concept_id=question.concept_id, mastery_after=m_after,
            next_decision_id="",  # filled by the route layer after DecisionService
        )


def _event(**kwargs) -> "object":
    """Build a LearnerEvent without importing at module import time (keeps
    the service importable by tooling without the Pydantic layer ready)."""
    from ..domain.schemas import LearnerEvent
    return LearnerEvent(**kwargs)


__all__ = ["AssessmentService"]
