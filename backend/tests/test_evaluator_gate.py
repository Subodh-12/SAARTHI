"""Test for Decision Quality Evaluator release gates (Design v2 Section 11.1 & 15).

Verifies:
- Evaluator returns 0 on the genuine gold scenarios dataset.
- Evaluator returns non-zero when any critical category (e.g. missing_pack_offline) fails its gate.
- Evaluator returns non-zero if structural validity is violated.
"""
import copy
import json
import pytest
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

from eval_decision_quality import evaluate_decision_quality, SCENARIOS_FILE


def test_evaluator_passes_on_gold_dataset():
    ret = evaluate_decision_quality(SCENARIOS_FILE)
    assert ret == 0, "Evaluator should return 0 on genuine gold dataset"


def test_evaluator_fails_on_missing_pack_offline_failure(tmp_path: Path):
    data = json.loads(SCENARIOS_FILE.read_text(encoding="utf-8"))
    bad_data = copy.deepcopy(data)
    # Corrupt expected in missing_pack_offline so it fails agreement
    for sc in bad_data["scenarios"]:
        if sc.get("category") == "missing_pack_offline":
            sc["expected"]["action"] = "IMPOSSIBLE_ACTION"

    bad_file = tmp_path / "bad_gold.json"
    bad_file.write_text(json.dumps(bad_data), encoding="utf-8")

    ret = evaluate_decision_quality(bad_file)
    assert ret != 0, "Evaluator must return nonzero when missing_pack_offline fails"


def test_evaluator_fails_on_structural_failure(tmp_path: Path):
    data = json.loads(SCENARIOS_FILE.read_text(encoding="utf-8"))
    bad_data = copy.deepcopy(data)
    # Corrupt input ruleset so engine returns invalid or error
    for sc in bad_data["scenarios"][:5]:
        sc["input"] = {}  # Empty input causing structural failure

    bad_file = tmp_path / "corrupt_gold.json"
    bad_file.write_text(json.dumps(bad_data), encoding="utf-8")

    ret = evaluate_decision_quality(bad_file)
    assert ret != 0, "Evaluator must return nonzero when structural validity fails"
