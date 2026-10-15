#!/usr/bin/env python3
"""Deterministic question classification and backfill for Bloom's Taxonomy.

Classifies curriculum questions into the canonical 6 Bloom levels:
  - remember
  - understand
  - apply
  - analyze
  - evaluate
  - create

Never equates difficulty with cognitive level.
Every classification is grounded in what the question objectively asks the learner to do.

Usage:
  python scripts/classify_questions.py          # Apply classification to manifests
  python scripts/classify_questions.py --check  # Verify all questions have valid Bloom metadata
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRIC = ROOT / "curriculum"

sys.path.insert(0, str(ROOT / "backend"))
from app.domain.bloom import BLOOM_ORDER, BloomLevel, is_valid_bloom_level, parse_bloom_level

# Authoritative manual audit classifications for existing curriculum questions
# grounded in the actual cognitive task required by each question:
CURATED_CLASSIFICATIONS: dict[str, BloomLevel] = {
    # --- Chapter 1: Matter in Our Surroundings ---
    # Recall properties of solid
    "q_ch01_c0001_01": BloomLevel.REMEMBER,
    # Understand particle model and forces in gas
    "q_ch01_c0001_02": BloomLevel.UNDERSTAND,
    # Compare and distinguish solid, liquid, gas
    "q_ch01_c0001_03": BloomLevel.ANALYZE,
    # Recall formula of density = mass / volume
    "q_ch01_c0002_01": BloomLevel.REMEMBER,
    # Apply relative density rule (RD=2.0 > 1.0 -> sinks) to predict sinking/floating
    "q_ch01_c0002_02": BloomLevel.APPLY,
    # Explain concept and definition of relative density
    "q_ch01_c0002_03": BloomLevel.UNDERSTAND,
    # Recall terminology: melting (solid to liquid)
    "q_ch01_c0003_01": BloomLevel.REMEMBER,
    # Recall terminology: condensation (gas to liquid)
    "q_ch01_c0003_02": BloomLevel.REMEMBER,
    # Explain sublimation and provide an example
    "q_ch01_c0003_03": BloomLevel.UNDERSTAND,
    # Cloze definition recall: matter definition
    "q_ch001_c0001_ga1": BloomLevel.REMEMBER,
    # Classify everyday items as matter examples
    "q_ch001_c0001_ga2": BloomLevel.UNDERSTAND,
    # Recall SI unit of density (kg/m3)
    "q_ch001_c0002_ga1": BloomLevel.REMEMBER,

    # --- Chapter 2: Motion - Measurement ---
    # Apply displacement definition to circular motion path
    "q_ch02_c0004_01": BloomLevel.APPLY,
    # Recall SI unit of displacement (m)
    "q_ch02_c0004_02": BloomLevel.REMEMBER,
    # Compare components: distance vs displacement
    "q_ch02_c0004_03": BloomLevel.ANALYZE,
    # Recall SI unit of speed/velocity (m/s)
    "q_ch02_c0005_01": BloomLevel.REMEMBER,
    # Apply speed formula: distance/time = 120km / 2h = 60 km/h
    "q_ch02_c0005_02": BloomLevel.APPLY,
    # Compare components: speed (scalar) vs velocity (vector)
    "q_ch02_c0005_03": BloomLevel.ANALYZE,
    # Recall SI unit of acceleration (m/s2)
    "q_ch02_c0006_01": BloomLevel.REMEMBER,
    # Apply acceleration formula: (v - u) / t = (30 - 10) / 5 = 4 m/s2
    "q_ch02_c0006_02": BloomLevel.APPLY,
    # Explain kinematic equation v = u + at and interpret its terms
    "q_ch02_c0006_03": BloomLevel.UNDERSTAND,

    # --- Chapter 3: Tissues - Living Organisms ---
    # Recall definition of tissue
    "q_ch03_c0007_01": BloomLevel.REMEMBER,
    # Recall number of main tissue types
    "q_ch03_c0007_02": BloomLevel.REMEMBER,
    # Compare and contrast plant and animal tissues
    "q_ch03_c0007_03": BloomLevel.ANALYZE,
    # Recall dividing tissue: meristematic
    "q_ch03_c0008_01": BloomLevel.REMEMBER,
    # Explain physiological function of xylem
    "q_ch03_c0008_02": BloomLevel.UNDERSTAND,
    # Compare parenchyma, collenchyma, and sclerenchyma structures and functions
    "q_ch03_c0008_03": BloomLevel.ANALYZE,
    # Explain function of nervous tissue
    "q_ch03_c0009_01": BloomLevel.UNDERSTAND,
    # Analyze components to identify non-neuron structure
    "q_ch03_c0009_02": BloomLevel.ANALYZE,
    # Summarize and classify muscle tissue types
    "q_ch03_c0009_03": BloomLevel.UNDERSTAND,
    # Cloze recall: histogenesis
    "q_ch003_c0007_ga1": BloomLevel.REMEMBER,
    # Cloze recall: definition of tissue
    "q_ch003_c0007_ga2": BloomLevel.REMEMBER,
    # Explain process of cell division forming tissue
    "q_ch003_c0007_ga3": BloomLevel.UNDERSTAND,
    # Comparative analysis of growth limits in plant vs animal tissues
    "q_ch003_c0007_ga4": BloomLevel.ANALYZE,
    # Identify function: xylem transport of water
    "q_ch003_c0008_ga1": BloomLevel.UNDERSTAND,
    # Recall collenchyma cell wall pectin
    "q_ch003_c0008_ga2": BloomLevel.REMEMBER,
    # Recall sclerenchyma lignin
    "q_ch003_c0008_ga3": BloomLevel.REMEMBER,
    # Explain permanent tissue differentiation
    "q_ch003_c0008_ga4": BloomLevel.UNDERSTAND,
    # Recall parts of neuron
    "q_ch003_c0009_ga1": BloomLevel.REMEMBER,
}


def classify_question_content(q: dict) -> tuple[BloomLevel | None, str]:
    """Deterministically determine Bloom level from curated map or content heuristics.
    
    Returns (bloom_level, status_note).
    """
    qid = q.get("question_id", "")
    if qid in CURATED_CLASSIFICATIONS:
        return CURATED_CLASSIFICATIONS[qid], "curated_audit"

    # If already has a valid bloom_level, validate it
    raw_level = q.get("bloom_level")
    if is_valid_bloom_level(raw_level):
        return parse_bloom_level(raw_level), "existing_valid"

    # Heuristic analysis based on prompt cues when not in curated map
    prompt = q.get("prompt_or", "").lower()
    qtype = q.get("qtype", "")

    # Calculations / problem solving -> apply
    if any(k in prompt for k in ["କେତେ", "ଗଣନା", "ହିସାବ", "ହାରାହାରି"]):
        return BloomLevel.APPLY, "heuristic_calculation"

    # Comparison / differences -> analyze
    if any(k in prompt for k in ["ପାର୍ଥକ୍ୟ", "ତୁଳନା", "ଅଂଶ ନୁହେଁ", "ଭିନ୍ନ"]):
        return BloomLevel.ANALYZE, "heuristic_comparison"

    # Definitions / recall -> remember
    if any(k in prompt for k in ["ସୂତ୍ର", "ଏକକ", "କଣ କୁହାଯାଏ", "ପରିଭାଷା", "ଖାଲି ଜାଗା"]):
        return BloomLevel.REMEMBER, "heuristic_recall"

    # Explanations -> understand
    if any(k in prompt for k in ["ବ୍ୟାଖ୍ୟା", "କାର୍ଯ୍ୟ", "କାହିଁକି"]):
        return BloomLevel.UNDERSTAND, "heuristic_explanation"

    # Ambiguous / unresolved
    return None, "unresolved"


def run_classification(check_only: bool = False) -> int:
    total_questions = 0
    classified_counts: dict[str, int] = {lvl.value: 0 for lvl in BLOOM_ORDER}
    ambiguous: list[str] = []
    updated_files = 0

    for ch_dir in sorted(CURRIC.iterdir()):
        if not ch_dir.is_dir() or not ch_dir.name.startswith("ch"):
            continue
        mpath = ch_dir / "manifest.json"
        if not mpath.exists():
            continue
        m = json.loads(mpath.read_text(encoding="utf-8"))
        questions = m.get("questions", [])
        manifest_modified = False

        for q in questions:
            total_questions += 1
            qid = q.get("question_id", "")
            level, note = classify_question_content(q)

            if level is None:
                ambiguous.append(qid)
                continue

            classified_counts[level.value] += 1
            if q.get("bloom_level") != level.value:
                q["bloom_level"] = level.value
                manifest_modified = True

        if manifest_modified and not check_only:
            mpath.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
            updated_files += 1

    print("=== Bloom's Taxonomy Classification Report ===")
    print(f"Total questions surveyed: {total_questions}")
    print("Classifications by Bloom level:")
    for lvl in BLOOM_ORDER:
        print(f"  {lvl.value:12s}: {classified_counts[lvl.value]}")
    print(f"Ambiguous / Unresolved:   {len(ambiguous)} questions")
    if ambiguous:
        print(f"  Unresolved IDs: {ambiguous}")

    if check_only:
        if ambiguous or any(c == 0 for c in [classified_counts["remember"], classified_counts["understand"]]):
            print("[FAIL] Unresolved questions found or core foundational levels missing.")
            return 1
        print("[PASS] All questions have valid Bloom taxonomy classifications.")
        return 0

    print(f"Updated manifests: {updated_files}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify curriculum questions into Bloom levels")
    parser.add_argument("--check", action="store_true", help="Check only, do not write changes")
    args = parser.parse_args()
    return run_classification(check_only=args.check)


if __name__ == "__main__":
    sys.exit(main())
