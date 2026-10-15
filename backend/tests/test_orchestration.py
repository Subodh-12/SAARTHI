"""Orchestration tests v2 — translation tool, retrieval, ordered validation,
extractive fallback, generation records."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "backend"))

os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{tempfile.mktemp(suffix='.db')}"
os.environ["PERSISTENCE_BACKEND"] = "sqlite"
os.environ["TRANSLATION_PROVIDER"] = "mock"
os.environ["LLM_PROVIDER"] = "mock"
os.environ["EMBEDDINGS_PROVIDER"] = "mock"

from app.adapters.ai.translation import MockTranslationProvider, get_translation_provider
from app.adapters.ai.retrieval import LocalHybridRetriever, get_retrieval_provider
from app.adapters.ai.generation import MockGenerationProvider, get_generation_provider
from app.domain.schemas import (
    DoubtRequest, GeneratedAnswer, RetrievedChunk, RetrievedResult, ToolError,
)
from app.orchestration.graph import PROMPT_VERSION, OrchestrationState, run_doubt
from app.orchestration import validators


def test_translation_mock_returns_typed_unavailable():
    provider = get_translation_provider()
    assert isinstance(provider, MockTranslationProvider)
    result = provider.translate.__wrapped__(provider, "hi", "or", "en") \
        if hasattr(provider.translate, "__wrapped__") else None
    import asyncio
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(provider.translate("hi", "or", "en"))
    finally:
        loop.close()
    assert isinstance(result, ToolError)
    assert result.error_code == "UNAVAILABLE"


def test_translation_passthrough_same_lang():
    provider = get_translation_provider()
    import asyncio
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(provider.translate("ପଦାର୍ଥ", "or", "or"))
    finally:
        loop.close()
    assert result.text == "ପଦାର୍ଥ"
    assert result.confidence == 1.0


def test_retrieval_local_hybrid_returns_chunks():
    provider = get_retrieval_provider()
    assert isinstance(provider, LocalHybridRetriever)
    import asyncio
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(provider.retrieve("ପଦାର୍ଥ କଣ", top_k=4))
    finally:
        loop.close()
    assert len(result.chunks) > 0
    assert result.provider == "local_hybrid"
    # RRF fusion caps results at the ruleset top_k.
    assert len(result.chunks) <= 4


def test_generation_mock_returns_extractive():
    provider = get_generation_provider()
    assert isinstance(provider, MockGenerationProvider)
    chunks = [RetrievedChunk(
        chunk_id="chunk_ch01_c0001_01", concept_id="c0001", chapter_id="ch001",
        text_or="ପଦାର୍ଥ ହେଉଛି ସବୁ ଯାହାର ଭାର ଅଛି।", source_ref="ch01 §1.2",
        score=0.8, matched_terms=[],
    )]
    from app.adapters.ai.interfaces import GenerationRequest
    import asyncio
    loop = asyncio.new_event_loop()
    try:
        text, citations, err = loop.run_until_complete(
            provider.generate(GenerationRequest(query="ପଦାର୍ଥ କଣ", retrieved_chunks=chunks)))
    finally:
        loop.close()
    assert err is None
    assert "ପଦାର୍ଥ" in text
    assert citations == ["chunk_ch01_c0001_01"]


@pytest.mark.asyncio
async def test_orchestration_doubt_odia_query():
    """End-to-end doubt orchestration with an Odia query: translation tool is
    skipped for pure-Odia input (never forced on every query)."""
    resp = await run_doubt(DoubtRequest(
        query="ପଦାର୍ଥ କଣ?", learner_id="lrn_0123456789abcdef", pack_ids=[],
    ))
    assert resp.answer.text_or
    assert resp.retrieved.chunks
    assert resp.used_translation_tool is False
    assert resp.decision_id
    # Every generation produces a generation record (v2 Section 4/7).
    record = resp.generation_record
    assert record is not None
    assert record.prompt_version == PROMPT_VERSION
    assert record.prompt_hash
    assert record.chunk_ids  # the retrieved chunks that fed the answer
    assert record.validation_results.get("ok") is True
    assert isinstance(record.fallback_used, bool)


@pytest.mark.asyncio
async def test_orchestration_translation_called_for_latin_query():
    """Latin-script query triggers translate_text (typed unavailable; the
    graph continues with the original query)."""
    resp = await run_doubt(DoubtRequest(
        query="What is matter in science?", learner_id="lrn_0123456789abcdef",
        pack_ids=[],
    ))
    assert resp.used_translation_tool is True


@pytest.mark.asyncio
async def test_orchestration_code_mixed_query_skips_translation_when_odia_dominant():
    resp = await run_doubt(DoubtRequest(
        query="ପଦାର୍ଥ ଏବଂ ଅଣୁ କଣ?", learner_id="lrn_0123456789abcdef", pack_ids=[],
    ))
    assert resp.used_translation_tool is False


@pytest.mark.asyncio
async def test_extractive_answer_passes_ordered_validation():
    chunk = RetrievedChunk(
        chunk_id="chunk_ch01_c0001_01", concept_id="c0001", chapter_id="ch001",
        text_or="ପଦାର୍ଥ ହେଉଛି ସବୁ ଯାହାର ଭାର ଅଛି।",
        source_ref="ch01 §1.2", score=0.9, matched_terms=[],
    )
    answer = GeneratedAnswer(
        text_or="ପଦାର୍ଥ ହେଉଛି ସବୁ ଯାହାର ଭାର ଅଛି।",
        citations=["chunk_ch01_c0001_01"], chapter_refs=["ch001"],
        confidence=0.9, provenance="extractive",
    )
    retrieved = RetrievedResult(chunks=[chunk], provider="local_hybrid",
                                confidence=0.9)
    verdict = await validators.validate_answer_full(answer, retrieved,
                                                    entailer=None)
    assert verdict.ok, f"failed gate: {verdict.failed_gate}"
    assert verdict.gates_passed == ["schema", "source_references",
                                    "language_length", "safety", "grounding"]


def test_validation_unknown_citation_fails():
    answer = GeneratedAnswer(
        text_or="ଉତ୍ତର", citations=["chunk_does_not_exist_xx"],
        chapter_refs=["ch001"], confidence=0.5, provenance="extractive",
    )
    retrieved = RetrievedResult(chunks=[], provider="none", confidence=0)
    verdict = validators.validate_answer(answer, retrieved)
    assert not verdict.ok
    assert verdict.failed_gate == "source.unknown_chunk_id"


def test_validation_low_odia_ratio_fails():
    answer = GeneratedAnswer(
        text_or="This is an English answer not in Odia",
        citations=["chunk_ch01_c0001_01"], chapter_refs=["ch001"],
        confidence=0.5, provenance="llm_grounded",
    )
    retrieved = RetrievedResult(chunks=[RetrievedChunk(
        chunk_id="chunk_ch01_c0001_01", concept_id="c0001", chapter_id="ch001",
        text_or="ପଦାର୍ଥ", source_ref="ch01 §1.2", score=0.9, matched_terms=[])],
        provider="local_hybrid", confidence=0.9)
    verdict = validators.validate_answer(answer, retrieved)
    assert not verdict.ok
    assert verdict.failed_gate == "language.odia_ratio_low"


def test_validation_out_of_lessons_passes():
    answer = GeneratedAnswer(
        text_or="ଏହି ପ୍ରଶ୍ନ ଆମ ପାଠ୍ୟକ୍ରମରେ ନାହିଁ।",
        citations=[], chapter_refs=[], confidence=0.0, provenance="basic",
        basic_answer_status="out_of_lessons",
    )
    retrieved = RetrievedResult(chunks=[], provider="none", confidence=0)
    verdict = validators.validate_answer(answer, retrieved)
    assert verdict.ok, f"failed: {verdict.failed_gate}"
