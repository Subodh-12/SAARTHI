"""Unit and contract tests for generated-answer grounding and entailment.

Design Document v2 Sections 4.6, 5, 12, 13.
"""
from __future__ import annotations

import pytest

from app.adapters.ai.entailment import (
    DeterministicSentenceEntailer,
    ModelEntailer,
    extract_content_tokens,
    extract_odia_sentences,
)
from app.adapters.ai.interfaces import EntailmentVerdict


def test_extract_odia_sentences():
    text = "ପଦାର୍ଥ କ୍ଷୁଦ୍ର କଣିକା ଦ୍ୱାରା ଗଠିତ। ଏହି କଣିକାଗୁଡ଼ିକ ମଧ୍ୟରେ ଫାଙ୍କା ସ୍ଥାନ ଥାଏ। ତାହା କିପରି ସମ୍ଭବ?"
    sentences = extract_odia_sentences(text)
    assert len(sentences) == 3
    assert "ପଦାର୍ଥ କ୍ଷୁଦ୍ର କଣିକା ଦ୍ୱାରା ଗଠିତ" in sentences[0]


def test_extract_content_tokens():
    text = "କଠିନ ପଦାର୍ଥର ଏକ ନିର୍ଦ୍ଦିଷ୍ଟ ଆକାର ଏବଂ ଆୟତନ ଥାଏ।"
    tokens = extract_content_tokens(text)
    assert "କଠିନ" in tokens
    assert "ପଦାର୍ଥର" in tokens
    assert "ଆକାର" in tokens
    assert "ଆୟତନ" in tokens
    assert "ଏବଂ" not in tokens  # stopword stripped


@pytest.mark.asyncio
async def test_entailer_accepts_supported_claims():
    entailer = DeterministicSentenceEntailer()
    source_chunk = (
        "ଆମ ଚାରିପାଖରେ ଥିବା ସମସ୍ତ ବସ୍ତୁ ପଦାର୍ଥ ଦ୍ୱାରା ଗଠିତ। ପଦାର୍ଥ କ୍ଷୁଦ୍ର କଣିକାଗୁଡ଼ିକ ଦ୍ୱାରା ଗଠିତ। "
        "ଏହି କଣିକାଗୁଡ଼ିକ ମଧ୍ୟରେ ଆନ୍ତଃ-କଣିକା ଆକର୍ଷଣ ବଳ କାର୍ଯ୍ୟ କରେ। କଠିନ ପଦାର୍ଥର ନିର୍ଦ୍ଦିଷ୍ଟ ଆକାର ଓ ଆୟତନ ଥାଏ।"
    )
    answer = "ପଦାର୍ଥ କ୍ଷୁଦ୍ର କଣିକାଗୁଡ଼ିକ ଦ୍ୱାରା ଗଠିତ। ଏହି କଣିକାଗୁଡ଼ିକ ମଧ୍ୟରେ ଆନ୍ତଃ-କଣିକା ଆକର୍ଷଣ ବଳ ଥାଏ।"

    verdict = await entailer.entail(answer, [source_chunk])
    assert verdict.supported is True
    assert verdict.confidence >= 0.7
    assert "verified" in verdict.detail


@pytest.mark.asyncio
async def test_entailer_rejects_unsupported_factual_claim():
    entailer = DeterministicSentenceEntailer()
    source_chunk = (
        "କଠିନ ପଦାର୍ଥର ଏକ ନିର୍ଦ୍ଦିଷ୍ଟ ଆକାର ଏବଂ ଆୟତନ ଥାଏ। କଣିକାଗୁଡ଼ିକ ଦୃଢ଼ ଭାବରେ ଆବଦ୍ଧ ଥାଆନ୍ତି।"
    )
    # Fabricated claim about temperature and rocket propulsion not found in chunk
    unsupported_answer = (
        "କଠିନ ପଦାର୍ଥର ଏକ ନିର୍ଦ୍ଦିଷ୍ଟ ଆକାର ଥାଏ। ରକେଟ୍ ପ୍ରପଲସନ୍ ଇଞ୍ଜିନ୍ ୫୦୦୦ ଡିଗ୍ରୀ ତାପମାତ୍ରାରେ ଚାଲେ।"
    )

    verdict = await entailer.entail(unsupported_answer, [source_chunk])
    assert verdict.supported is False
    assert "unsupported factual claim" in verdict.detail


@pytest.mark.asyncio
async def test_entailer_rejects_empty_chunks():
    entailer = DeterministicSentenceEntailer()
    verdict = await entailer.entail("କୌଣସି ଉତ୍ତର।", [])
    assert verdict.supported is False
    assert "no source chunks cited" in verdict.detail


@pytest.mark.asyncio
async def test_model_entailer_fallback_without_credentials(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    from app.core.settings import reset_settings_cache
    reset_settings_cache()

    entailer = ModelEntailer()
    source_chunk = "ପଦାର୍ଥ କ୍ଷୁଦ୍ର କଣିକାଗୁଡ଼ିକ ଦ୍ୱାରା ଗଠିତ।"
    answer = "ପଦାର୍ଥ କ୍ଷୁଦ୍ର କଣିକା ଦ୍ୱାରା ଗଠିତ।"
    verdict = await entailer.entail(answer, [source_chunk])
    assert verdict.supported is True
