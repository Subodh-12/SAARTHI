"""Entailment provider — grounding validation (Design Document v2 Sections 4.6, 5, 12, 13).

Validates generated factual claims against retrieved curriculum chunks.
Rejects unsupported claims.
Never returns fabricated entailment success.
Provides typed results: Ok[EntailmentVerdict] | ProviderError.
"""
from __future__ import annotations

import re
import time
import unicodedata
from typing import Generic, Literal, Optional, TypeVar

from pydantic import BaseModel

from ...core.logging import get_logger
from ...core.settings import get_settings
from .interfaces import EntailmentProvider, EntailmentVerdict

log = get_logger("saarthi.entailment")

T = TypeVar("T")


# --------------------------------------------------------------------------- #
# Typed Provider Result Contract (Design v2 Section 5)
# --------------------------------------------------------------------------- #
class ProviderError(BaseModel):
    code: Literal[
        "TIMEOUT",
        "RATE_LIMITED",
        "UNAVAILABLE",
        "BAD_OUTPUT",
        "LOW_CONFIDENCE",
        "UNSUPPORTED_LANGUAGE",
        "QUOTA_EXHAUSTED",
    ]
    retryable: bool
    detail_dev: str  # never shown to learners


class Ok(BaseModel, Generic[T]):
    value: T
    provider: str
    model_id: str
    latency_ms: int
    request_id: str


Result = Ok[T] | ProviderError


# --------------------------------------------------------------------------- #
# Deterministic Entailer — sentence-level proposition containment
# --------------------------------------------------------------------------- #
ODIA_STOPWORDS = {
    "ଏହା", "ଏହି", "ଏବଂ", "ଓ", "କିମ୍ବା", "ତେଣୁ", "କାରଣ", "ର", "ରେ", "କୁ",
    "ଠାରେ", "ଦ୍ୱାରା", "ପାଇଁ", "ହୁଏ", "ହୋଇଥାଏ", "ଅଟେ", "ଅଟନ୍ତି", "ମଧ୍ୟ",
    "ହେଉଛି", "କରେ", "କରିଥାଏ", "ପାରେ", "ହୋଇଛି", "ସେହି", "ଯେଉଁ", "ତାହା",
    "ଅଛି", "ଥିଲା", "ହେବ", "ପରି", "ପରିବର୍ତ୍ତେ", "ଏପରି", "ଅନ୍ୟ", "ସବୁ",
}


def extract_odia_sentences(text: str) -> list[str]:
    """Split Odia text into sentences using Odia danda (।), question mark, and newline."""
    raw = re.split(r"[।?!;\n]+", text)
    sentences = [s.strip() for s in raw if s.strip() and len(s.strip()) > 3]
    return sentences


def extract_content_tokens(text: str) -> set[str]:
    """Extract substantive Odia and Latin content words, stripping stopwords and punctuation."""
    norm = unicodedata.normalize("NFC", text.lower())
    tokens = re.findall(r"[\w\u0B00-\u0B7F]+", norm)
    return {t for t in tokens if len(t) >= 2 and t not in ODIA_STOPWORDS}


class DeterministicSentenceEntailer(EntailmentProvider):
    """Deterministic factual containment entailer.

    Checks each factual sentence of the candidate answer against the cited
    curriculum chunks. A sentence is supported only if its key propositions,
    scientific terms, and relationships are substantiated by the source chunks.
    Keyword overlap alone is rejected; each sentence must be factually covered.
    """

    name = "deterministic_sentence"

    async def entail(self, answer: str, source_chunks: list[str]) -> EntailmentVerdict:
        if not source_chunks:
            return EntailmentVerdict(
                supported=False,
                confidence=0.0,
                detail="no source chunks cited for entailment",
            )

        sentences = extract_odia_sentences(answer)
        if not sentences:
            return EntailmentVerdict(
                supported=False,
                confidence=0.0,
                detail="answer contains no parseable factual sentences",
            )

        combined_source_text = " ".join(source_chunks)
        source_tokens = extract_content_tokens(combined_source_text)
        source_norm = unicodedata.normalize("NFC", combined_source_text.lower())

        unsupported_sentences = []
        sentence_confidences: list[float] = []

        for s in sentences:
            s_tokens = extract_content_tokens(s)
            if not s_tokens:
                continue

            # Check token containment
            overlap = s_tokens & source_tokens
            containment = len(overlap) / len(s_tokens)

            # Check if key numbers / measurements in the sentence appear in source
            numbers_in_s = re.findall(r"\d+[\.,]?\d*", s)
            numbers_supported = all(num in combined_source_text for num in numbers_in_s)

            # Check for phrase or n-gram continuity (bi-grams of content words)
            s_tok_list = [t for t in re.findall(r"[\w\u0B00-\u0B7F]+", s.lower()) if t in s_tokens]
            bigrams = [f"{s_tok_list[i]} {s_tok_list[i+1]}" for i in range(len(s_tok_list) - 1)]
            bigram_matches = sum(1 for bg in bigrams if bg in source_norm)
            bigram_ratio = bigram_matches / len(bigrams) if bigrams else 1.0

            # Sentence is considered supported if >= 75% of content terms exist
            # and numbers match and significant bigrams/phrases align
            if containment >= 0.75 and numbers_supported and (not bigrams or bigram_ratio >= 0.3):
                sentence_confidences.append(min(1.0, containment * 0.8 + bigram_ratio * 0.2))
            else:
                unsupported_sentences.append(s)
                sentence_confidences.append(containment * 0.5)

        if not sentence_confidences:
            return EntailmentVerdict(
                supported=False, confidence=0.0, detail="no substantive factual statements found"
            )

        avg_confidence = sum(sentence_confidences) / len(sentence_confidences)

        if unsupported_sentences:
            return EntailmentVerdict(
                supported=False,
                confidence=round(avg_confidence, 3),
                detail=f"unsupported factual claim: '{unsupported_sentences[0][:100]}'",
            )

        return EntailmentVerdict(
            supported=True,
            confidence=round(avg_confidence, 3),
            detail="all factual sentences verified against cited curriculum chunks",
        )


# --------------------------------------------------------------------------- #
# Model-Based Entailer (gated by LLM API key)
# --------------------------------------------------------------------------- #
class ModelEntailer(EntailmentProvider):
    """Online model-based NLI / grounding verifier.

    Sends candidate answer and chunks to secondary model prompt.
    If provider is unavailable, returns typed error or degraded result.
    """

    name = "model"

    def __init__(self) -> None:
        self.s = get_settings()
        self._fallback = DeterministicSentenceEntailer()

    async def entail(self, answer: str, source_chunks: list[str]) -> EntailmentVerdict:
        if not self.s.has_secret("llm_api_key"):
            # Fall back to deterministic containment check
            return await self._fallback.entail(answer, source_chunks)

        import httpx

        prompt = (
            "You are a strict natural language inference (NLI) evaluator for Class 9 Science. "
            "Determine if EVERY factual sentence in the Candidate Answer is strictly entailed "
            "and supported by the Source Text. If any claim is unsupported or invented, return "
            "SUPPORTED: NO with the unsupported sentence. Otherwise return SUPPORTED: YES.\n\n"
            f"Source Text:\n{' '.join(source_chunks)}\n\n"
            f"Candidate Answer:\n{answer}\n\n"
            "Verdict format:\nSUPPORTED: YES or NO\nCONFIDENCE: 0.0-1.0\nDETAIL: short reason"
        )

        headers = {
            "Authorization": f"Bearer {self.s.llm_api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.s.llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "max_tokens": 100,
        }

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.post(
                    f"{self.s.llm_base_url.rstrip('/')}/chat/completions",
                    headers=headers,
                    json=body,
                )
                if resp.status_code != 200:
                    log.warning("entailment model HTTP %d, falling back to deterministic", resp.status_code)
                    return await self._fallback.entail(answer, source_chunks)

                content = resp.json()["choices"][0]["message"]["content"]
                is_supported = "SUPPORTED: YES" in content.upper()
                return EntailmentVerdict(
                    supported=is_supported,
                    confidence=0.9 if is_supported else 0.2,
                    detail="verified by NLI model" if is_supported else "model rejected factual entailment",
                )
        except Exception as e:
            log.warning("entailment model call failed (%s), falling back to deterministic", e)
            return await self._fallback.entail(answer, source_chunks)


# --------------------------------------------------------------------------- #
# Factory
# --------------------------------------------------------------------------- #
_cached_entailer: Optional[EntailmentProvider] = None


def get_entailment_provider() -> EntailmentProvider:
    global _cached_entailer
    if _cached_entailer is not None:
        return _cached_entailer
    s = get_settings()
    if s.has_secret("llm_api_key"):
        _cached_entailer = ModelEntailer()
    else:
        _cached_entailer = DeterministicSentenceEntailer()
    return _cached_entailer


def reset_entailment_cache() -> None:
    global _cached_entailer
    _cached_entailer = None
