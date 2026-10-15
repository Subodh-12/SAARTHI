"""Canonical Bloom's Taxonomy definitions and helpers for SAARTHI.

Ordered from lower to higher cognitive complexity:
  1. remember   - recall facts, definitions, terminology, and formulas
  2. understand - explain ideas, interpret information, summarize, or classify examples
  3. apply      - use knowledge, rules, or formulas to solve a problem in a new situation
  4. analyze    - distinguish components, identify relationships, compare evidence, and diagnose errors
  5. evaluate   - judge claims, compare approaches, and justify conclusions using evidence
  6. create     - develop an original solution, model, investigation, or explanation

Stable machine-readable identifiers with Odia-first learner-facing labels.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Optional

BLOOM_TAXONOMY_VERSION = "1.0.0"


class BloomLevel(str, Enum):
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"


# Canonical order of cognitive complexity
BLOOM_ORDER: tuple[BloomLevel, ...] = (
    BloomLevel.REMEMBER,
    BloomLevel.UNDERSTAND,
    BloomLevel.APPLY,
    BloomLevel.ANALYZE,
    BloomLevel.EVALUATE,
    BloomLevel.CREATE,
)

BLOOM_LEVEL_INDEX: dict[str, int] = {
    lvl.value: idx for idx, lvl in enumerate(BLOOM_ORDER)
}

# Learner-facing labels in Odia and English
BLOOM_LABELS_OR: dict[BloomLevel, str] = {
    BloomLevel.REMEMBER: "ମନେରଖିବା",
    BloomLevel.UNDERSTAND: "ବୁଝିବା",
    BloomLevel.APPLY: "ପ୍ରୟୋଗ",
    BloomLevel.ANALYZE: "ବିଶ୍ଳେଷଣ",
    BloomLevel.EVALUATE: "ମୂଲ୍ୟାଙ୍କନ",
    BloomLevel.CREATE: "ନିର୍ମାଣ",
}

BLOOM_LABELS_EN: dict[BloomLevel, str] = {
    BloomLevel.REMEMBER: "Remember",
    BloomLevel.UNDERSTAND: "Understand",
    BloomLevel.APPLY: "Apply",
    BloomLevel.ANALYZE: "Analyze",
    BloomLevel.EVALUATE: "Evaluate",
    BloomLevel.CREATE: "Create",
}

# Simple, learner-friendly objective descriptions
BLOOM_DESCRIPTIONS_OR: dict[BloomLevel, str] = {
    BloomLevel.REMEMBER: "ତଥ୍ୟ, ସଂଜ୍ଞା ଓ ସୂତ୍ର ମନେପକାଅ",
    BloomLevel.UNDERSTAND: "ଧାରଣା ବୁଝ ଓ ନିଜ ଭାଷାରେ ବ୍ୟାଖ୍ୟା କର",
    BloomLevel.APPLY: "ନୂତନ ପରିସ୍ଥିତିରେ ନିୟମ ଓ ସୂତ୍ର ପ୍ରୟୋଗ କର",
    BloomLevel.ANALYZE: "ଅଂଶଗୁଡ଼ିକ ତୁଳନା କର ଓ ସମ୍ପର୍କ ଚିହ୍ନଟ କର",
    BloomLevel.EVALUATE: "ପ୍ରମାଣ ଆଧାରରେ ଯୁକ୍ତି ଓ ସିଦ୍ଧାନ୍ତର ବିଚାର କର",
    BloomLevel.CREATE: "ନୂତନ ସମାଧାନ, ମଡେଲ ବା ପରିକଳ୍ପନା ତିଆରି କର",
}

BLOOM_DESCRIPTIONS_EN: dict[BloomLevel, str] = {
    BloomLevel.REMEMBER: "Recall facts, definitions, terminology, and formulas",
    BloomLevel.UNDERSTAND: "Explain ideas, interpret information, or classify examples",
    BloomLevel.APPLY: "Use rules or formulas to solve problems in new situations",
    BloomLevel.ANALYZE: "Distinguish components, compare evidence, and diagnose errors",
    BloomLevel.EVALUATE: "Assess claims, compare approaches, and justify judgments",
    BloomLevel.CREATE: "Develop an original solution, model, or explanation",
}


def is_valid_bloom_level(value: Any) -> bool:
    """Check if value is a valid canonical Bloom level identifier."""
    if isinstance(value, BloomLevel):
        return True
    if not isinstance(value, str):
        return False
    return value.strip().lower() in BLOOM_LEVEL_INDEX


def parse_bloom_level(value: Any) -> BloomLevel:
    """Parse and normalize value into a BloomLevel enum member. Raises ValueError if invalid."""
    if isinstance(value, BloomLevel):
        return value
    if isinstance(value, str):
        cleaned = value.strip().lower()
        if cleaned in BLOOM_LEVEL_INDEX:
            return BloomLevel(cleaned)
    raise ValueError(f"Invalid Bloom taxonomy level: {value!r}. Must be one of {[lvl.value for lvl in BLOOM_ORDER]}")


def bloom_complexity(level: BloomLevel | str) -> int:
    """Return 0-indexed cognitive complexity rank (0=remember, 5=create)."""
    val = level.value if isinstance(level, BloomLevel) else str(level).strip().lower()
    if val not in BLOOM_LEVEL_INDEX:
        raise ValueError(f"Unknown Bloom level: {level!r}")
    return BLOOM_LEVEL_INDEX[val]


def compare_bloom(a: BloomLevel | str, b: BloomLevel | str) -> int:
    """Compare complexity: -1 if a < b, 0 if a == b, 1 if a > b."""
    ca, cb = bloom_complexity(a), bloom_complexity(b)
    if ca < cb:
        return -1
    if ca > cb:
        return 1
    return 0


def next_higher_level(level: BloomLevel | str) -> Optional[BloomLevel]:
    """Return the next higher cognitive complexity level, or None if already at create."""
    idx = bloom_complexity(level)
    if idx + 1 < len(BLOOM_ORDER):
        return BLOOM_ORDER[idx + 1]
    return None


def next_lower_level(level: BloomLevel | str) -> Optional[BloomLevel]:
    """Return the next lower cognitive complexity level, or None if already at remember."""
    idx = bloom_complexity(level)
    if idx > 0:
        return BLOOM_ORDER[idx - 1]
    return None


def bloom_label(level: BloomLevel | str, lang: str = "or") -> str:
    """Return human-readable learner-facing label."""
    lvl = parse_bloom_level(level)
    if lang.lower().startswith("en"):
        return BLOOM_LABELS_EN.get(lvl, lvl.value.capitalize())
    return BLOOM_LABELS_OR.get(lvl, lvl.value)


def bloom_description(level: BloomLevel | str, lang: str = "or") -> str:
    """Return learner-friendly objective description."""
    lvl = parse_bloom_level(level)
    if lang.lower().startswith("en"):
        return BLOOM_DESCRIPTIONS_EN.get(lvl, "")
    return BLOOM_DESCRIPTIONS_OR.get(lvl, "")


__all__ = [
    "BLOOM_TAXONOMY_VERSION",
    "BloomLevel",
    "BLOOM_ORDER",
    "BLOOM_LEVEL_INDEX",
    "BLOOM_LABELS_OR",
    "BLOOM_LABELS_EN",
    "BLOOM_DESCRIPTIONS_OR",
    "BLOOM_DESCRIPTIONS_EN",
    "is_valid_bloom_level",
    "parse_bloom_level",
    "bloom_complexity",
    "compare_bloom",
    "next_higher_level",
    "next_lower_level",
    "bloom_label",
    "bloom_description",
]
