"""Diagnosis service — glue between the pure diagnosis/verification modules
and repositories. Derives everything deterministically from the (idempotent)
event history, mastery records, and the pack; stores nothing itself.
"""
from __future__ import annotations

from typing import Optional

from ..content.pack_loader import PackContentIndex
from ..domain.diagnose import Diagnosis, diagnose_concept, diagnose_submission
from ..domain.schemas import LearnerEvent, MasteryRecord, Question
from ..domain.verification import TagEvidence, verification_status
from ..repositories import EventRepository, MasteryRepository

# Events retained for verification evidence derivation (small window).
EVIDENCE_WINDOW = 50


def _tag_evidence_for_concept(
    pack: PackContentIndex, events: list[LearnerEvent], concept_id: str,
) -> list[TagEvidence]:
    out: list[TagEvidence] = []
    for ev in events:
        if ev.concept_id != concept_id or not ev.question_id:
            continue
        if ev.payload.get("evidence") == "none":
            continue  # unanswered never contributes
        q = pack.questions.get(ev.question_id)
        if q is None:
            continue
        sel = ev.payload.get("selected_option")
        if sel is not None and q.correct_option is not None and sel != q.correct_option:
            tag = (q.misconception_options.get(str(sel), "")
                   or (q.misconception_tag or "")).strip()
            out.append(TagEvidence(question_id=ev.question_id, tag=tag,
                                   evidence=ev.payload.get("evidence", "none")))
        elif ev.payload.get("evidence") == "correct":
            # A correct answer counts against every tag the question maps:
            # the learner avoided all of those candidate misconceptions.
            mapped = {t.strip() for t in q.misconception_options.values() if t.strip()}
            if q.misconception_tag:
                mapped.add(q.misconception_tag.strip())
            for t in mapped or {""}:
                out.append(TagEvidence(question_id=ev.question_id, tag=t,
                                       evidence="correct"))
    return out


def diagnose_from_history(
    pack: PackContentIndex,
    question: Question,
    selected_option: Optional[int],
    concept_events: list[LearnerEvent],
    mastery_records: list[MasteryRecord],
) -> dict:
    """Build the diagnosis payload attached to an assessment result.

    Combines the current response with prior concept evidence: candidate
    causes, a discriminating follow-up (never a repeated/answered question),
    and the verification-gate status. Privacy: only question IDs, tags and
    counts — never raw answer text.
    """
    concept_questions = [q for q in pack.questions.values()
                         if q.concept_id == question.concept_id]
    recently_answered = {ev.question_id for ev in concept_events
                         if ev.question_id and ev.question_id != question.question_id}
    prereqs = pack.prereqs.get(question.concept_id, [])
    prereq_ok = bool(prereqs) and all(
        any(m.concept_id == p and m.p_known >= 0.5 for m in mastery_records)
        for p in prereqs)

    base = diagnose_submission(
        question, selected_option,
        recently_answered=recently_answered,
        concept_questions=concept_questions,
        prereq_correct_recently=prereq_ok,
    )
    # Concept-level merge over prior evidence (excluding the current question —
    # retries at the same question must not double-count) + the current response:
    prior = [(pack.questions[ev.question_id], ev.payload.get("selected_option"))
             for ev in concept_events
             if ev.question_id in pack.questions
             and ev.concept_id == question.concept_id
             and ev.question_id != question.question_id]
    concept_diag = diagnose_concept(
        prior + [(question, selected_option)],
        recently_answered=recently_answered,
        prereq_correct_recently=prereq_ok,
        concept_questions=concept_questions,
    )
    return _merge(base, concept_diag, pack, concept_events, question.concept_id,
                  mastery_records)


def _merge(base: Diagnosis, concept_diag: Optional[Diagnosis],
           pack: PackContentIndex, events: list[LearnerEvent], concept_id: str,
           mastery_records: list[MasteryRecord]) -> dict:
    evidences = _tag_evidence_for_concept(pack, events, concept_id)
    status = verification_status(evidences)
    diag = concept_diag if (base.status == "candidate" and concept_diag) else base
    causes_payload = [
        {
            "tag": c.tag,
            "label_or": c.label_or,
            "label_en": c.label_en,
            "pending_teacher_review": c.pending_teacher_review,
            "supporting": list(c.supporting),
            "contradicting": list(c.contradicting),
        } for c in diag.causes
    ]
    return {
        "status": diag.status,
        "causes": causes_payload,
        "followup_question_id": diag.followup_question_id,
        "verification_status": status,
        "note_or": diag.note_or,
        "note_en": diag.note_en,
    }


class DiagnosisService:
    def __init__(self, pack: PackContentIndex, events: EventRepository,
                 mastery: MasteryRepository) -> None:
        self.pack = pack
        self.events = events
        self.mastery = mastery

    async def for_submission(self, learner_id: str, question: Question,
                             selected_option: Optional[int],
                             current_concept_events: Optional[list[LearnerEvent]] = None,
                             mastery_records: Optional[list[MasteryRecord]] = None) -> Optional[dict]:
        if question.qtype != "mcq" or selected_option is None:
            return None
        if question.correct_option is not None and selected_option == question.correct_option:
            return None
        if current_concept_events is None or mastery_records is None:
            all_events = await self.events.list_events(learner_id, since_seq=0)
            mastery_records = await self.mastery.get_mastery(learner_id)
            current_concept_events = [
                ev for ev in all_events[-EVIDENCE_WINDOW:]
                if ev.concept_id == question.concept_id]
        return diagnose_from_history(
            self.pack, question, selected_option,
            current_concept_events, mastery_records)
