"""Cause-aware misconception diagnosis — pure functions over explicit inputs.

Extends (does not replace) the deterministic decision engine: BKT and
next-action selection in `decide.py` are untouched; this module only produces
candidate causes and a discriminating follow-up suggestion. Mastery
integration and verification gating are layered on later (Phase 5).

Design constraints:
  - One incorrect answer is NEVER treated as a diagnosed misconception. The
    output is a *candidate* cause with explicit evidence, or an explicit
    insufficient-evidence state.
  - Distractor→misconception mappings are teacher-authored metadata on the
    question (`Question.misconception_options`). Tags without a catalog entry
    are surfaced as pending teacher review, never invented.
  - Deterministic: candidates ordered by (evidence strength desc, tag asc);
    follow-up selection tie-breaks by question_id ascending and never repeats
    a recently answered question.
  - Pure data in, pure data out — no I/O, no LLM.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .schemas import Question

# Teacher-reviewed misconception catalog. Tags NOT listed here are still
# reported (with the tag string) but flagged as pending teacher review.
MISCONCEPTION_CATALOG: dict[str, dict[str, str]] = {
    "relative_density_float": {
        "label_or": "ଅପେକ୍ଷା ଘନତ୍ୱ ୧ରୁ ଅଧିକ ଥିଲେ ମଧ୍ୟ ବସ୍ତୁ ଭାସେ ବୋଲି ଭ୍ରାନ୍ତ ଧାରଣା",
        "label_en": "Believes objects with relative density greater than 1 still float",
    },
    "density_ratio_inverted": {
        "label_or": "ଘନତ୍ୱର ଅନୁପାତ ଓଲଟାଇ ଲେଖେ (ଆୟତନ / ଭର)",
        "label_en": "Inverts the density ratio (volume / mass instead of mass / volume)",
    },
    "displacement_zero_in_circular": {
        "label_or": "ବୃତ୍ତାକାର ଗତିରେ ଅପସରଣ ଶୂନ ହୁଏ ବୋଲି ଅଜ୍ଞାନତା",
        "label_en": "Does not treat displacement as zero after a full circular path",
    },
    "neuron_vs_matrix": {
        "label_or": "ନ୍ୟୁରନ୍ ଓ ମାଟ୍ରିକ୍ସ (ଆଧାର ପଦାର୍ଥ) ମଧ୍ୟରେ ଗଣ୍ଡି ମିଶାଏ",
        "label_en": "Mixes up neurons with the matrix (ground substance) of tissue",
    },
}

PENDING_REVIEW_OR = "ଏହି କାରଣ ଚିହ୍ନଟ ଶିକ୍ଷକ ପରୀକ୍ଷା ଅପେକ୍ଷାରେ ଅଛି।"
PENDING_REVIEW_EN = "This candidate cause is pending teacher review."


@dataclass
class DiagnosisCause:
    tag: str
    label_or: str
    label_en: str
    pending_teacher_review: bool
    supporting: list[str] = field(default_factory=list)   # evidence statements
    contradicting: list[str] = field(default_factory=list)


@dataclass
class Diagnosis:
    status: str  # "correct" | "candidate" | "insufficient_evidence" | "unsupported"
    causes: list[DiagnosisCause] = field(default_factory=list)
    followup_question_id: Optional[str] = None
    note_or: str = ""
    note_en: str = ""


def _cause(tag: str, supporting: list[str], contradicting: list[str]) -> DiagnosisCause:
    entry = MISCONCEPTION_CATALOG.get(tag)
    if entry:
        return DiagnosisCause(tag=tag, label_or=entry["label_or"],
                              label_en=entry["label_en"],
                              pending_teacher_review=False,
                              supporting=supporting, contradicting=contradicting)
    return DiagnosisCause(tag=tag,
                          label_or=f"ଅଜଣା ଭ୍ରାନ୍ତି ଚିହ୍ନ: {tag} — {PENDING_REVIEW_OR}",
                          label_en=f"Unknown misconception tag: {tag} — {PENDING_REVIEW_EN}",
                          pending_teacher_review=True,
                          supporting=supporting, contradicting=contradicting)


def diagnose_submission(
    question: Question,
    selected_option: Optional[int],
    recently_answered: set[str] = frozenset(),
    concept_questions: Optional[list[Question]] = None,
    prereq_correct_recently: bool = False,
) -> Diagnosis:
    """Diagnose candidate causes for one MCQ response.

    Args:
        question: the answered question (with optional distractor mapping).
        selected_option: index chosen; None/short-answer ⇒ unsupported.
        recently_answered: question_ids to avoid for the follow-up.
        concept_questions: other questions on the same concept (for follow-up
            selection); when omitted, no follow-up is selected.
        prereq_correct_recently: True when the learner recently answered
            prerequisite concepts correctly — recorded as contradicting
            evidence against a foundational-gap cause.
    """
    concept_questions = concept_questions or []
    if question.qtype != "mcq" or question.correct_option is None:
        return Diagnosis(status="unsupported",
                         note_or="ଏହି ପ୍ରଶ୍ନ ପାଇଁ ବିକଳ୍ପ ଆଧାରିତ ରୋଗନିର୍ଣ୍ଣୟ ସମ୍ଭବ ନୁହେଁ।",
                         note_en="Option-based diagnosis is not available for this question type.")
    if selected_option is None:
        return Diagnosis(status="unsupported",
                         note_or="ଉତ୍ତର ଦିଆଯାଇ ନାହିଁ — ଅନୁତ୍ତରିତ ପ୍ରଶ୍ନ ଭୁଲ ବୋଲି ଗଣାଯାଏ ନାହିଁ।",
                         note_en="No answer was given — unanswered is not counted as incorrect.")
    if selected_option == question.correct_option:
        return Diagnosis(status="correct")

    raw = question.misconception_options.get(str(selected_option), "")
    tag = raw.strip() or (question.misconception_tag or "").strip()

    supporting = [f"Selected incorrect option {selected_option} on {question.question_id}"]
    contradicting: list[str] = []
    if prereq_correct_recently:
        contradicting.append("Recently answered prerequisite concepts correctly — "
                             "a foundational gap is less likely.")

    if not tag:
        return Diagnosis(
            status="insufficient_evidence",
            note_or="ଏହି ଭୁଲ ପାଇଁ କୌଣସି ଚିହ୍ନିତ କାରଣ ମ୍ୟାପିଙ୍ଗ ନାହିଁ — ଅଧିକ ପ୍ରମାଣ ଆବଶ୍ୟକ।",
            note_en="No teacher-authored cause is mapped for this incorrect option; "
                    "more evidence is needed before claiming a cause.",
        )

    causes = [_cause(tag, supporting, list(contradicting))]

    followup = select_followup(
        [tag], concept_questions, exclude={question.question_id, *recently_answered})
    return Diagnosis(status="candidate", causes=causes, followup_question_id=followup)


def diagnose_concept(
    responses: list[tuple[Question, Optional[int]]],
    recently_answered: set[str] = frozenset(),
    prereq_correct_recently: bool = False,
    concept_questions: Optional[list[Question]] = None,
) -> Diagnosis:
    """Diagnose across multiple responses on the same concept.

    Merges per-response candidate tags into competing causes: each distinct
    tag accumulates the responses that support it. A single distinct tag is
    one candidate; several distinct tags are competing candidates that a
    discriminating follow-up should separate.
    """
    if not responses:
        return Diagnosis(status="insufficient_evidence",
                         note_or="ପ୍ରମାଣ ନାହିଁ।", note_en="No evidence available.")
    first = responses[0][0]
    if any(q.qtype != "mcq" or q.correct_option is None for q, _ in responses):
        return Diagnosis(status="unsupported",
                         note_or="ବିକଳ୍ପ ଆଧାରିତ ରୋଗନିର୍ଣ୍ଣୟ ସମ୍ଭବ ନୁହେଁ।",
                         note_en="Option-based diagnosis is not available for these questions.")

    supporting: dict[str, list[str]] = {}
    any_unmapped = False
    any_answered = False
    for q, sel in responses:
        if sel is None:
            continue  # unanswered is not incorrect evidence
        any_answered = True
        if sel == q.correct_option:
            continue
        tag = q.misconception_options.get(str(sel), "").strip() or \
            (q.misconception_tag or "").strip()
        if tag:
            supporting.setdefault(tag, []).append(
                f"Selected incorrect option {sel} on {q.question_id}")
        else:
            any_unmapped = True

    if not any_answered:
        return Diagnosis(status="insufficient_evidence",
                         note_or="କୌଣସି ଉତ୍ତର ମିଳିଲା ନାହିଁ।",
                         note_en="No answered evidence available.")
    if not supporting:
        return Diagnosis(
            status="insufficient_evidence",
            note_or="ଭୁଲ ଉତ୍ତର ପାଇଁ ଚିହ୍ନିତ କାରଣ ମ୍ୟାପିଙ୍ଗ ନାହିଁ — ଅଧିକ ପ୍ରମାଣ ଆବଶ୍ୟକ।",
            note_en="Incorrect answers have no teacher-authored cause mapping; "
                    "more evidence is needed.")

    contradicting = []
    if prereq_correct_recently:
        contradicting.append("Recently answered prerequisite concepts correctly — "
                             "a foundational gap is less likely.")
    causes = [_cause(tag, ev, list(contradicting))
              for tag, ev in sorted(supporting.items())]  # deterministic: tag asc
    tags = sorted(supporting.keys())
    exclude = {q.question_id for q, _ in responses} | set(recently_answered)
    pool = concept_questions if concept_questions is not None else [q for q, _ in responses]
    followup = select_followup(tags, pool, exclude=exclude)
    note_en = ("Multiple candidate causes remain — the suggested follow-up "
               "helps distinguish them." if len(causes) > 1 else "")
    return Diagnosis(status="candidate", causes=causes,
                     followup_question_id=followup, note_en=note_en,
                     note_or=("ଏକାଧିକ ସମ୍ଭାବ୍ୟ କାରଣ ରହିଛି — ପରବର୍ତ୍ତୀ ପ୍ରଶ୍ନ ସେମାନଙ୍କୁ ଅଲଗା କରିବ।"
                              if len(causes) > 1 else ""))


def select_followup(
    candidate_tags: list[str],
    concept_questions: list[Question],
    exclude: set[str] = frozenset(),
) -> Optional[str]:
    """Pick the question that best discriminates the candidate tags.

    Preference order (deterministic):
      1. Unexcluded MCQs whose distractor mapping contains exactly one of the
         candidate tags (discriminates between competing causes), tie-break by
         question_id ascending.
      2. Otherwise any unexcluded MCQ on the concept, tie-break by question_id.
      3. None when everything is excluded — no repetition.
    """
    candidates = [q for q in concept_questions
                  if q.qtype == "mcq" and q.question_id not in exclude]
    discriminating, neutral = [], []
    tags = set(candidate_tags)
    for q in sorted(candidates, key=lambda q: q.question_id):
        mapped = {v.strip() for v in q.misconception_options.values()}
        overlap = mapped & tags
        if len(overlap) == 1 and len(mapped) > 1:
            discriminating.append(q.question_id)
        else:
            neutral.append(q.question_id)
    if discriminating:
        return discriminating[0]
    if neutral:
        return neutral[0]
    return None


__all__ = [
    "Diagnosis",
    "DiagnosisCause",
    "MISCONCEPTION_CATALOG",
    "diagnose_submission",
    "diagnose_concept",
    "select_followup",
]
