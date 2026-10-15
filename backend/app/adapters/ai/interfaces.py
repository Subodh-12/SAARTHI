"""AI provider interfaces — typed contracts.

Each provider returns either a typed success result or a typed ToolError.
Adapters live below; the orchestration graph depends on these interfaces.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Optional

from ...domain.schemas import RetrievedChunk, RetrievedResult, ToolError


# --------------------------------------------------------------------------- #
# Translation
# --------------------------------------------------------------------------- #
@dataclass
class TranslationResult:
    text: str
    source_lang: str
    target_lang: str
    provider: str
    model_id: Optional[str] = None
    confidence: float = 0.8
    used_cache: bool = False


class TranslationProvider(abc.ABC):
    name: str = "abstract"
    @abc.abstractmethod
    async def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult | ToolError: ...
    @abc.abstractmethod
    async def health(self) -> dict: ...


# --------------------------------------------------------------------------- #
# Embeddings
# --------------------------------------------------------------------------- #
class EmbeddingsProvider(abc.ABC):
    name: str = "abstract"
    @abc.abstractmethod
    async def embed(self, texts: list[str]) -> tuple[list[list[float]], Optional[ToolError]]: ...
    @abc.abstractmethod
    def dim(self) -> int: ...


# --------------------------------------------------------------------------- #
# Retrieval
# --------------------------------------------------------------------------- #
class RetrievalProvider(abc.ABC):
    name: str = "abstract"
    @abc.abstractmethod
    async def retrieve(self, query: str, top_k: int = 5,
                       pack_ids: Optional[list[str]] = None) -> RetrievedResult: ...


# --------------------------------------------------------------------------- #
# Generation
# --------------------------------------------------------------------------- #
@dataclass
class GenerationRequest:
    query: str
    retrieved_chunks: list[RetrievedChunk]
    system_prompt: Optional[str] = None
    max_answer_chars: int = 1200


class GenerationProvider(abc.ABC):
    name: str = "abstract"
    @abc.abstractmethod
    async def generate(self, req: GenerationRequest) -> tuple[str, list[str], Optional[ToolError]]:
        """Return (answer_text, citation_chunk_ids, error)."""


# --------------------------------------------------------------------------- #
# Entailment (grounding validation — Design v2 Section 13 gate 5)
# --------------------------------------------------------------------------- #
@dataclass
class EntailmentVerdict:
    supported: bool
    confidence: float = 0.0
    detail: str = ""


class EntailmentProvider(abc.ABC):
    """Model-based grounding check. Keyword overlap is NEVER a substitute.
    When unavailable, the caller must fall back to a labelled extractive
    answer or a safe redirect (never show unverified generated text)."""
    name: str = "abstract"
    @abc.abstractmethod
    async def entail(self, answer: str, source_chunks: list[str]) -> EntailmentVerdict: ...


__all__ = [
    "TranslationProvider", "TranslationResult",
    "EmbeddingsProvider",
    "RetrievalProvider",
    "GenerationProvider", "GenerationRequest",
    "EntailmentProvider", "EntailmentVerdict",
]
