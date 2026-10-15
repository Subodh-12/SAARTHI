"""Translation providers — Mock + HuggingFace IndicTrans2 (Section 4.1).

Contract (Design v2 Sections 4, 5, 12):
- Translation is an ORCHESTRATION TOOL behind a typed provider interface,
  exposed to the LangGraph workflow as the whitelisted tool
  `translate_text`. It is used only where translation materially helps
  (Latin-script Odia, code-mixed queries, glossary term normalisation) —
  never forced on every query, and never allowed to alter the meaning of
  cited curriculum content or invent educational facts.
- The deterministic learning-action engine never depends on it.

IndicTrans2 integration (real inference procedure):
- Models: `ai4bharat/indictrans2-en-indic-dist-200M` (en→indic) and
  `ai4bharat/indictrans2-indic-en-dist-200M` (indic→en), configurable.
- Language identifiers are the flores-200 codes the models were trained
  with: `eng_Latn` and `ory_Odia` (v1 wrongly used `en_Indic`).
- The official IndicProcessor performs the REQUIRED preprocessing
  (normalisation + script conversion) and postprocessing; the adapter
  falls back to a minimal IndicNLP-based pre/post-processing when the
  official package is unavailable, and reports the degraded mode in
  `health()` instead of pretending full fidelity.
- Model identifiers, device selection, precision, timeouts, cache paths
  and credentials are configurable (Settings: HF_*). The model is loaded
  ONCE per process and cached translations are bounded — a large model is
  never re-downloaded per request.
- HF credentials come from the environment (HF_TOKEN) or an approved
  secret mechanism; a missing token is a typed, non-fatal error: the
  offline learning path never requires a Hugging Face credential.
- Typed errors cover download failures, access restrictions (gated repo),
  missing weights, unsupported language pairs and inference errors.

When credentials or model access are unavailable the provider returns
typed errors; the provider CONTRACT is what the tests verify. Mock tests
do NOT prove the model works — real inference remains unverified without
credentials.
"""
from __future__ import annotations

import functools
import hashlib
import re
import time
import unicodedata
from typing import Optional

from ...core.logging import get_logger
from ...core.settings import get_settings
from ...domain.schemas import ToolError
from .interfaces import TranslationProvider, TranslationResult

log = get_logger("saarthi.translation")

# flores-200 language codes used by IndicTrans2 (v2 fix — v1 used
# "en_Indic", which the models do not understand).
FLORES_CODES = {
    "or": "ory_Odia",
    "odia": "ory_Odia",
    "ory": "ory_Odia",
    "en": "eng_Latn",
}

# Language pairs the IndicTrans2 distilled models actually support.
SUPPORTED_PAIRS = {
    ("en", "or"),   # en-indic model
    ("or", "en"),   # indic-en model
}


def typed_error(code: str, detail: str, provider: str,
                model_id: Optional[str] = None,
                retryable: bool = False) -> ToolError:
    """Map internal failure modes onto the v2 provider error codes."""
    allowed = {"TIMEOUT", "RATE_LIMITED", "UNAVAILABLE", "BAD_OUTPUT",
               "LOW_CONFIDENCE", "UNSUPPORTED_LANGUAGE", "QUOTA_EXHAUSTED",
               "ACCESS_RESTRICTED", "MODEL_DOWNLOAD_FAILED", "MISSING_WEIGHTS"}
    return ToolError(
        error_code=code if code in allowed else "UNAVAILABLE",  # type: ignore[arg-type]
        detail_dev=detail,
        provider=provider, model_id=model_id, retryable=retryable,
    )


class MockTranslationProvider(TranslationProvider):
    """Returns a typed `UNAVAILABLE` ToolError for any non-trivial request.

    This is the mandated behaviour when model access is gated or
    credentials are absent — translation is never faked. A passthrough for
    already-Odia text is provided so orchestration can normalise without an
    extra round-trip.
    """
    name = "mock"

    def __init__(self) -> None:
        self.s = get_settings()

    async def translate(self, text: str, source_lang: str,
                        target_lang: str) -> TranslationResult | ToolError:
        if source_lang == target_lang:
            return TranslationResult(
                text=text, source_lang=source_lang, target_lang=target_lang,
                provider=self.name, model_id=None, confidence=1.0, used_cache=False,
            )
        return typed_error(
            "UNAVAILABLE",
            "TRANSLATION_PROVIDER=mock — set TRANSLATION_PROVIDER=hf_local "
            "(and HF_TOKEN for the gated IndicTrans2 repos). The offline "
            "learning path does not require translation.",
            self.name)

    async def health(self) -> dict:
        return {
            "provider": self.name,
            "ready": False,
            "model_id": None,
            "reason": "TRANSLATION_PROVIDER=mock; no model loaded",
        }


class _IndicPrePost:
    """IndicTrans2 preprocessing/postprocessing.

    Prefers the official `IndicProcessor` (pip `IndicTrans2` / the AI4Bharat
    repo's common module). Falls back to IndicNLP normalisation + a minimal
    post-processor; `full_fidelity` reports which path is active so
    diagnostics stay honest.
    """

    def __init__(self) -> None:
        self.ip = None
        self.full_fidelity = False
        self._indicnlp_ready = False
        try:
            from IndicTrans2 import IndicProcessor  # type: ignore
            self.ip = IndicProcessor(inference_mode="bulk")
            self.full_fidelity = True
        except Exception:  # noqa: BLE001 — optional dependency
            try:
                from indicnlp.normalize.indic_normalize import IndicNormalizerFactory
                self._normalizer_factory = IndicNormalizerFactory()
                self._indicnlp_ready = True
            except Exception:  # noqa: BLE001
                self._indicnlp_ready = False

    def preprocess(self, text: str, src_flores: str) -> str:
        text = unicodedata.normalize("NFC", text)
        if self.ip is not None:
            try:
                batch = self.ip.preprocess_batch([text], src=src_flores,
                                                 tgt="ory_Odia"
                                                 if src_flores == "eng_Latn" else "eng_Latn")
                return batch[0]
            except Exception:  # noqa: BLE001 — fall through to minimal path
                log.warning("indic_processor_preprocess_failed — minimal path used")
        if self._indicnlp_ready and src_flores == "ory_Odia":
            try:
                normalizer = self._normalizer_factory.get_normalizer("or")
                return normalizer.normalize(text)
            except Exception:  # noqa: BLE001
                pass
        return re.sub(r"\s+", " ", text).strip()

    def postprocess(self, text: str, src_flores: str, tgt_flores: str) -> str:
        if self.ip is not None:
            try:
                batch = self.ip.postprocess_batch([text], lang=tgt_flores)
                return batch[0]
            except Exception:  # noqa: BLE001
                pass
        return text.strip()


class HuggingFaceTranslationProvider(TranslationProvider):
    """Real adapter for AI4Bharat IndicTrans2 distilled models.

    Loads lazily and ONCE per process; honours configured device/precision/
    cache paths/credentials; every failure mode returns a typed error.
    """
    name = "hf_local"

    def __init__(self) -> None:
        self.s = get_settings()
        self._model_en2indic = None
        self._model_indic2en = None
        self._tokenizer_en2indic = None
        self._tokenizer_indic2en = None
        self._pp = _IndicPrePost()
        self._load_attempted = False
        self._load_error: Optional[str] = None
        # Bounded cache keyed by (text, src, tgt)
        self._cache: dict[str, tuple[str, float]] = {}
        self._cache_max = int(getattr(self.s, "translation_cache_max_entries", 1024)
                              or 1024)

    # ---- language identifiers ---------------------------------------------
    @staticmethod
    def _flores(lang: str) -> Optional[str]:
        return FLORES_CODES.get(lang.strip().lower())

    @staticmethod
    def _base_lang(flores_or_plain: str) -> Optional[str]:
        l = flores_or_plain.strip().lower()
        if l in ("or", "odia", "ory", "ory_odia"):
            return "or"
        if l in ("en", "eng", "eng_latn"):
            return "en"
        return None

    # ---- model loading ------------------------------------------------------
    def _resolve_device(self):
        import torch
        pref = (self.s.hf_device or "auto").lower()
        if pref == "cpu":
            return "cpu"
        if pref == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("HF_DEVICE=cuda requested but CUDA is unavailable")
        if pref == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return pref

    def _resolve_dtype(self, device: str):
        import torch
        prec = (self.s.hf_precision or "auto").lower()
        if prec == "fp16":
            return torch.float16
        if prec == "fp32":
            return torch.float32
        return torch.float16 if device == "cuda" else torch.float32

    def _load_kwargs(self) -> dict:
        import os
        kwargs: dict = {}
        cache_dir = self.s.hf_cache_dir or os.environ.get("HF_HOME") or None
        if cache_dir:
            kwargs["cache_dir"] = cache_dir
        if self.s.has_secret("hf_token"):
            kwargs["token"] = self.s.hf_token
        kwargs["trust_remote_code"] = True
        return kwargs

    async def _ensure_loaded(self) -> Optional[ToolError]:
        if self._load_attempted:
            if self._model_en2indic is not None and self._model_indic2en is not None:
                return None
            return self._load_error_result()
        self._load_attempted = True
        if not self.s.has_secret("hf_token"):
            self._load_error = "HF_TOKEN not set; provide HF_TOKEN to access HuggingFace translation models."
            log.warning("hf_translation_token_missing")
            return self._load_error_result()
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            import torch  # noqa: F401
        except Exception as e:  # noqa: BLE001
            self._load_error = f"transformers/torch unavailable: {type(e).__name__}: {e}"
            log.warning("hf_translation_deps_missing err=%s", e)
            return self._load_error_result()
        device = self._resolve_device()
        dtype = self._resolve_dtype(device)
        kwargs = self._load_kwargs()
        log.info("hf_translation_loading device=%s dtype=%s en2indic=%s indic2en=%s",
                 device, dtype, self.s.hf_translation_model_en2indic,
                 self.s.hf_translation_model_indic2en)
        try:
            self._model_en2indic = AutoModelForSeq2SeqLM.from_pretrained(
                self.s.hf_translation_model_en2indic,
                torch_dtype=dtype, **kwargs).to(device).eval()
            self._tokenizer_en2indic = AutoTokenizer.from_pretrained(
                self.s.hf_translation_model_en2indic, **kwargs)
            self._model_indic2en = AutoModelForSeq2SeqLM.from_pretrained(
                self.s.hf_translation_model_indic2en,
                torch_dtype=dtype, **kwargs).to(device).eval()
            self._tokenizer_indic2en = AutoTokenizer.from_pretrained(
                self.s.hf_translation_model_indic2en, **kwargs)
        except OSError as e:
            msg = str(e)
            if "401" in msg or "403" in msg or "gated" in msg.lower() or "access" in msg.lower():
                self._load_error = ("access restricted: accept the gated repo "
                                    f"conditions and set HF_TOKEN — {msg[:300]}")
                log.warning("hf_translation_access_restricted")
            elif "connection" in msg.lower() or "timed out" in msg.lower() or "download" in msg.lower():
                self._load_error = f"model download failed: {msg[:300]}"
                log.warning("hf_translation_download_failed")
            else:
                self._load_error = f"weights unavailable: {msg[:300]}"
                log.warning("hf_translation_weights_missing")
            return self._load_error_result()
        except Exception as e:  # noqa: BLE001
            self._load_error = f"{type(e).__name__}: {e}"
            log.warning("hf_translation_load_failed err=%s", e)
            return self._load_error_result()
        log.info("hf_translation_loaded")
        return None

    def _load_error_result(self) -> ToolError:
        detail = self._load_error or "IndicTrans2 unavailable"
        code = "UNAVAILABLE"
        low = detail.lower()
        if "access restricted" in low:
            code = "ACCESS_RESTRICTED"
        elif "download failed" in low:
            code = "MODEL_DOWNLOAD_FAILED"
        elif "weights unavailable" in low:
            code = "MISSING_WEIGHTS"
        return typed_error(code, detail, self.name, retryable=False)

    # ---- translation ----------------------------------------------------------
    async def translate(self, text: str, source_lang: str,
                        target_lang: str) -> TranslationResult | ToolError:
        src_base = self._base_lang(source_lang)
        tgt_base = self._base_lang(target_lang)
        if src_base is None or tgt_base is None:
            return typed_error(
                "UNSUPPORTED_LANGUAGE",
                f"unsupported language identifier: {source_lang!r}/{target_lang!r} "
                f"(supported: or, en)",
                self.name)
        if (src_base, tgt_base) not in SUPPORTED_PAIRS:
            return typed_error(
                "UNSUPPORTED_LANGUAGE",
                f"unsupported language pair: {src_base}->{tgt_base} "
                "(IndicTrans2 supports en->or and or->en here)",
                self.name)
        if src_base == tgt_base:
            return TranslationResult(
                text=text, source_lang=src_base, target_lang=tgt_base,
                provider=self.name, confidence=1.0)
        if not self.s.has_secret("hf_token"):
            return typed_error(
                "UNAVAILABLE",
                "HF_TOKEN not set; the IndicTrans2 repos are gated. The offline "
                "learning path does not require translation.",
                self.name)
        err = await self._ensure_loaded()
        if err is not None:
            return err
        # Bound input length
        max_chars = int(getattr(self.s, "translation_max_input_chars", 500) or 500)
        if len(text) > max_chars:
            text = text[:max_chars]
        # Cache
        key = hashlib.sha256(f"{src_base}|{tgt_base}|{text}".encode("utf-8")).hexdigest()
        cached = self._cache.get(key)
        if cached:
            return TranslationResult(
                text=cached[0], source_lang=src_base, target_lang=tgt_base,
                provider=self.name, used_cache=True, confidence=0.9)
        import torch
        if src_base == "en":
            model, tok = self._model_en2indic, self._tokenizer_en2indic
            src_flores, tgt_flores = "eng_Latn", "ory_Odia"
            model_id = self.s.hf_translation_model_en2indic
        else:
            model, tok = self._model_indic2en, self._tokenizer_indic2en
            src_flores, tgt_flores = "ory_Odia", "eng_Latn"
            model_id = self.s.hf_translation_model_indic2en
        try:
            pre = self._pp.preprocess(text, src_flores)
            inputs = tok(pre, return_tensors="pt", truncation=True,
                         max_length=256).to(model.device)
            # IndicTrans2 NLLB-style target forcing: the target flores code is
            # a special token used as the forced BOS id.
            bos_id = None
            try:
                bos_id = tok.convert_tokens_to_ids(tgt_flores)
            except Exception:  # noqa: BLE001
                bos_id = None
            if not bos_id or bos_id == tok.unk_token_id:
                bos_id = getattr(tok, "lang_code_to_id", {}).get(tgt_flores)
            generate_kwargs: dict = {
                "max_length": 256, "num_beams": 4, "length_penalty": 0.8,
            }
            if bos_id:
                generate_kwargs["forced_bos_token_id"] = bos_id
            with torch.no_grad():
                out = model.generate(**inputs, **generate_kwargs)
            raw = tok.decode(out[0], skip_special_tokens=True)
            text_out = self._pp.postprocess(raw, src_flores, tgt_flores)
        except Exception as e:  # noqa: BLE001
            log.warning("hf_translation_inference_failed err=%s", e)
            return typed_error("UNAVAILABLE",
                               f"inference failed: {type(e).__name__}: {e}",
                               self.name, model_id=model_id, retryable=True)
        if not text_out.strip():
            return typed_error("BAD_OUTPUT", "model produced empty output",
                               self.name, model_id=model_id, retryable=True)
        if len(self._cache) >= self._cache_max:
            oldest = min(self._cache.items(), key=lambda kv: kv[1][1])
            del self._cache[oldest[0]]
        self._cache[key] = (text_out, time.time())
        return TranslationResult(
            text=text_out, source_lang=src_base, target_lang=tgt_base,
            provider=self.name, model_id=model_id, confidence=0.85)

    async def health(self) -> dict:
        return {
            "provider": self.name,
            "ready": (self._model_en2indic is not None
                      and self._model_indic2en is not None),
            "model_id_en2indic": self.s.hf_translation_model_en2indic,
            "model_id_indic2en": self.s.hf_translation_model_indic2en,
            "has_hf_token": self.s.has_secret("hf_token"),
            "load_attempted": self._load_attempted,
            "load_error": self._load_error,
            "full_fidelity_preprocessing": self._pp.full_fidelity,
            "real_inference_verified": False,
            "note": "real_inference_verified=true only after a live call "
                    "succeeds with credentials; mock tests never prove it",
        }


@functools.lru_cache(maxsize=1)
def get_translation_provider() -> TranslationProvider:
    s = get_settings()
    if s.translation_provider == "hf_local":
        return HuggingFaceTranslationProvider()
    return MockTranslationProvider()


def reset_translation_cache() -> None:
    get_translation_provider.cache_clear()


__all__ = [
    "MockTranslationProvider",
    "HuggingFaceTranslationProvider",
    "get_translation_provider",
    "reset_translation_cache",
    "typed_error",
    "FLORES_CODES",
    "SUPPORTED_PAIRS",
]
