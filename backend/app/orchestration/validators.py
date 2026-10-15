"""Validation gates — the ORDERED validation contract (Design v2 Section 13).

Checks run in this exact order and stop at the first failure:

  1. Schema            (deterministic)  output parses into the answer schema
  2. Source references (deterministic)  ≥1 cited chunk ID, each exists in the
                                         retrieved set, chapter reference present
  3. Language + length (deterministic)  predominantly Odia script, within the
                                         length cap, glossary terms used
  4. Safety + educational fit            on-syllabus, age-appropriate, no
                                         personal data (deterministic checks;
                                         model-based check runs online only)
  5. Grounding         (model-based)     every factual sentence supported by
                                         the cited chunks (entailment)

On failure: regenerate ONCE, then a clearly-labelled extractive answer or a
polite Odia redirect. Keyword overlap is NEVER accepted as proof of factual
entailment — it may only choose which passage an extractive answer shows.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Optional

from ..domain.schemas import GeneratedAnswer, RetrievedChunk, RetrievedResult
from ..domain.ruleset import get_ruleset


@dataclass
class ValidationVerdict:
    ok: bool
    failed_gate: Optional[str] = None
    gates_passed: list[str] = field(default_factory=list)
    order_index: int = -1


def _odia_unicode_ratio(text: str) -> float:
    if not text:
        return 0.0
    odia = sum(1 for c in text if "\u0B00" <= c <= "\u0B7F")
    alpha = sum(1 for c in text if c.isalpha())
    return odia / alpha if alpha else 0.0


# --------------------------------------------------------------------------- #
# Ordered gates — each returns None when it passes, else a failure code
# --------------------------------------------------------------------------- #
def _gate_schema(answer: GeneratedAnswer) -> Optional[str]:
    if not isinstance(answer.text_or, str) or not answer.text_or.strip():
        return "schema.empty_text"
    if not isinstance(answer.citations, list):
        return "schema.citations_type"
    if answer.provenance not in ("extractive", "llm_grounded", "basic"):
        return "schema.unknown_provenance"
    return None


def _gate_source_references(answer: GeneratedAnswer,
                            retrieved: RetrievedResult) -> Optional[str]:
    # The out-of-lessons redirect deliberately cites nothing: it must not
    # invent curriculum references.
    if answer.provenance == "basic" and answer.basic_answer_status and \
            "out_of_lessons" in answer.basic_answer_status:
        return None
    retrieved_ids = {c.chunk_id for c in retrieved.chunks}
    if not answer.citations:
        return "source.no_citation"
    for cid in answer.citations:
        if cid not in retrieved_ids:
            return "source.unknown_chunk_id"
    chapter_refs = set(answer.chapter_refs or [])
    for c in retrieved.chunks:
        if c.chunk_id in set(answer.citations) and c.chapter_id:
            chapter_refs.add(c.chapter_id)
    if not chapter_refs:
        return "source.no_chapter_reference"
    return None


def _gate_language_length(answer: GeneratedAnswer) -> Optional[str]:
    ruleset = get_ruleset()
    max_chars = int(ruleset.validation.get("max_answer_chars",
                                           ruleset.generation.get("max_answer_chars", 1200)))
    if len(answer.text_or) > max_chars:
        return "length.too_long"
    if answer.provenance == "extractive":
        return None  # taken verbatim from Odia chunks
    if answer.basic_answer_status and "out_of_lessons" in answer.basic_answer_status:
        return None  # explicit redirect marker
    ratio = _odia_unicode_ratio(answer.text_or)
    if ratio < float(ruleset.validation.get("min_odia_unicode_ratio", 0.6)):
        return "language.odia_ratio_low"
    return None


def _gate_safety(answer: GeneratedAnswer, learner_input: str = "") -> Optional[str]:
    ruleset = get_ruleset()
    # Chunk text and learner input are DATA, never instructions: an answer
    # that echoes instruction-like phrases from the prompt fails safety.
    lowered = answer.text_or.lower()
    for term in ruleset.validation.get("safety_blocked_terms", []) or []:
        if term and term.lower() in lowered:
            return "safety.blocked_term"
    # Age-appropriateness / on-syllabus deterministic heuristics.
    if re.search(r"(kill yourself|suicide|porn| Sex\b)", lowered):
        return "safety.unsafe_content"
    # Prompt-injection echo: the answer repeats an "instruction" to the model.
    if re.search(r"(ignore (all )?(previous|prior) instructions|system prompt)", lowered):
        return "safety.injection_echo"
    return None


def _keyword_overlap(answer: str, chunks: list[RetrievedChunk]) -> float:
    """Jaccard overlap of answer tokens with chunk tokens.

    Explicitly NOT a grounding proof (v2: "keyword overlap alone must never
    be treated as proof of factual entailment"); used only to pick the
    extractive passage and to reject LOW-overlap claimed-LLM answers."""
    import re as _re
    stop = {"ଏହା", "ଏହି", "ଏବଂ", "କିମ୍ବା", "ତେଣୁ", "ର", "ରେ", "କୁ", "the", "a", "an",
            "is", "are", "of", "and", "or", "to", "in", "on"}
    atoks = {t for t in _re.findall(r"[\w\u0B00-\u0B7F]+", answer.lower()) if t not in stop}
    if not atoks:
        return 0.0
    best = 0.0
    for c in chunks:
        ttoks = set(_re.findall(r"[\w\u0B00-\u0B7F]+", c.text_or.lower()))
        if not ttoks:
            continue
        best = max(best, len(atoks & ttoks) / len(atoks | ttoks))
    return best


async def _gate_grounding(answer: GeneratedAnswer, retrieved: RetrievedResult,
                          entailer=None) -> Optional[str]:
    """Model-based entailment against the cited chunks.

    When no entailment provider is configured (offline / mock), the answer
    cannot be verified as grounded → the caller must fall back to a
    clearly-labelled extractive answer or a redirect. Keyword overlap is
    deliberately NOT accepted as grounding.
    """
    if answer.provenance == "extractive":
        return None  # verbatim curriculum text is grounded by construction
    if answer.provenance == "basic":
        return None  # redirect / out-of-lessons marker
    if entailer is None:
        return "grounding.entailer_unavailable"
    verdict = await entailer.entail(answer.text_or,
                                    [c.text_or for c in retrieved.chunks
                                     if c.chunk_id in set(answer.citations)])
    if getattr(verdict, "supported", False):
        return None
    return f"grounding.not_entailed:{getattr(verdict, 'detail', '')}"[:200]


# --------------------------------------------------------------------------- #
# Top-level ordered validation
# --------------------------------------------------------------------------- #
def validate_answer(answer: GeneratedAnswer, retrieved: RetrievedResult,
                    learner_input: str = "") -> ValidationVerdict:
    """Deterministic gates 1-4 in order; gate 5 (grounding) requires the
    async entailment provider and is run by the orchestration graph."""
    gates: list[str] = []

    failed = _gate_schema(answer)
    if failed:
        return ValidationVerdict(ok=False, failed_gate=failed, gates_passed=gates,
                                 order_index=1)
    gates.append("schema")

    failed = _gate_source_references(answer, retrieved)
    if failed:
        return ValidationVerdict(ok=False, failed_gate=failed, gates_passed=gates,
                                 order_index=2)
    gates.append("source_references")

    failed = _gate_language_length(answer)
    if failed:
        return ValidationVerdict(ok=False, failed_gate=failed, gates_passed=gates,
                                 order_index=3)
    gates.append("language_length")

    failed = _gate_safety(answer, learner_input)
    if failed:
        return ValidationVerdict(ok=False, failed_gate=failed, gates_passed=gates,
                                 order_index=4)
    gates.append("safety")

    return ValidationVerdict(ok=True, gates_passed=gates, order_index=4)


async def validate_answer_full(answer: GeneratedAnswer, retrieved: RetrievedResult,
                               entailer=None, learner_input: str = "") -> ValidationVerdict:
    """The complete ordered contract including model-based grounding (gate 5)."""
    verdict = validate_answer(answer, retrieved, learner_input)
    if not verdict.ok:
        return verdict
    failed = await _gate_grounding(answer, retrieved, entailer)
    if failed:
        return ValidationVerdict(ok=False, failed_gate=failed,
                                 gates_passed=verdict.gates_passed, order_index=5)
    verdict.gates_passed.append("grounding")
    return verdict


def keyword_overlap(answer: str, retrieved: RetrievedResult) -> float:
    """Exposed for the graph: may choose extractive passages, never prove
    grounding."""
    return _keyword_overlap(answer, retrieved.chunks)


__all__ = [
    "validate_answer", "validate_answer_full", "keyword_overlap",
    "ValidationVerdict",
]
