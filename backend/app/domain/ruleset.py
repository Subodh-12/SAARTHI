"""Versioned ruleset loader.

The ruleset is the single source of truth for the deterministic learning
engine (Design v2 Appendix A). Python and TypeScript consume the SAME JSON
file via their respective loaders; both expose the same ``Ruleset`` shape so
shared test vectors can be applied. An unknown ruleset version is reported
as a typed error and produces the fallback decision (never a crash).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


class UnknownRulesetError(Exception):
    """Typed error: the supplied ruleset version is not known to this engine."""

    def __init__(self, ruleset_version: str) -> None:
        super().__init__(f"unknown ruleset version: {ruleset_version!r}")
        self.ruleset_version = ruleset_version


@dataclass
class Ruleset:
    raw: dict[str, Any]
    version: str
    ruleset_version: str
    bkt_version: str
    bkt: dict
    bands: dict
    guard: dict
    mastery: dict
    repetition_guard: dict
    target_selection: dict
    network: dict
    delivery: dict
    background_actions: dict
    retries: dict
    sync: dict
    pack: dict
    prefetch: dict
    doubt: dict
    auth: dict
    orchestration: dict
    translation: dict
    retrieval: dict
    generation: dict
    validation: dict
    bloom: dict = None  # type: ignore

    def __post_init__(self):
        if self.bloom is None:
            self.bloom = self.raw.get("bloom", {})

    def is_known(self) -> bool:
        return bool(self.ruleset_version)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_ruleset_path(path: str | os.PathLike | None = None) -> Path:
    configured = path or os.environ.get("SAARTHI_RULESET_PATH")
    if configured is None:
        default_path = _project_root() / "packages" / "ruleset" / "rules.json"
        return default_path
    candidate = Path(configured)
    if candidate.is_absolute():
        return candidate
    repo_root = _project_root()
    repo_candidate = repo_root / candidate
    if repo_candidate.exists():
        return repo_candidate
    cwd_candidate = Path.cwd() / candidate
    if cwd_candidate.exists():
        return cwd_candidate
    return repo_candidate


def load_ruleset(path: str | os.PathLike | None = None) -> Ruleset:
    resolved_path = _resolve_ruleset_path(path)
    with open(resolved_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return _from_raw(raw)


def _from_raw(raw: dict[str, Any]) -> Ruleset:
    return Ruleset(
        raw=raw,
        version=str(raw.get("version", raw.get("ruleset_version", ""))),
        ruleset_version=str(raw.get("ruleset_version", raw.get("version", ""))),
        bkt_version=str(raw.get("bkt_version", "1")),
        bkt=raw.get("bkt", {}),
        bands=raw.get("bands", raw.get("mastery", {}).get("thresholds", {})),
        guard=raw.get("guard", raw.get("repetition_guard", {})),
        mastery=raw.get("mastery", {}),
        repetition_guard=raw.get("repetition_guard", raw.get("guard", {})),
        target_selection=raw.get("target_selection", {}),
        network=raw.get("network", {}),
        delivery=raw.get("delivery", {}),
        background_actions=raw.get("background_actions", {}),
        retries=raw.get("retries", {}),
        sync=raw.get("sync", {}),
        pack=raw.get("pack", {}),
        prefetch=raw.get("prefetch", {}),
        doubt=raw.get("doubt", {}),
        auth=raw.get("auth", {}),
        orchestration=raw.get("orchestration", {}),
        translation=raw.get("translation", {}),
        retrieval=raw.get("retrieval", {}),
        generation=raw.get("generation", {}),
        validation=raw.get("validation", {}),
        bloom=raw.get("bloom", {}),
    )


@lru_cache(maxsize=4)
def get_ruleset(path: str | None = None) -> Ruleset:
    return load_ruleset(path)


def ruleset_from_dict(raw: dict[str, Any]) -> Ruleset:
    """Build a Ruleset from an in-memory dict (tests, generated vectors)."""
    return _from_raw(raw)


def reset_ruleset_cache() -> None:
    get_ruleset.cache_clear()


def mastery_band(p_bp: int, mastery: dict | None = None, ruleset: Ruleset | None = None) -> str:
    """v2 bands from basis points: weak / partial / mastered."""
    src = ruleset.bands if ruleset is not None else (mastery or {})
    weak_below = int((src.get("weak_below_bp")
                      if isinstance(src.get("weak_below_bp"), int)
                      else (src.get("thresholds", {}) or {}).get("weak_below_bp", 4000)))
    mastered_at = int((src.get("mastered_at_bp")
                       if isinstance(src.get("mastered_at_bp"), int)
                       else (src.get("thresholds", {}) or {}).get("mastered_at_bp", 8500)))
    if p_bp < weak_below:
        return "weak"
    if p_bp < mastered_at:
        return "partial"
    return "mastered"


__all__ = [
    "Ruleset", "UnknownRulesetError", "load_ruleset", "get_ruleset",
    "ruleset_from_dict", "reset_ruleset_cache", "mastery_band",
]
