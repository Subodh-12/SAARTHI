"""Shared v2 rule vectors — Python side.

Loads `tests/fixtures/rule_vectors.json` (produced by
`scripts/gen_rule_vectors.py`) and verifies the Python decision engine:
  - `golden`  : hand-labelled scenarios (the generator asserts these against
                the engine before writing, so they are spec labels, not
                snapshots)
  - `invalid` : invalid inputs where the fallback decision is required
  - `fuzz`    : engine snapshots; the TypeScript suite must return the exact
                same outputs for identical inputs (parity, v2 Section 15)
  - `bkt`     : step-by-step integer BKT sequences (also run by TypeScript)
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.domain.bkt import bkt_update_bp, mastery_band_bp, round_half_up_div
from app.domain.decide import (
    DecisionInput, MasteryEntry, RecentEvent, decide, engine_error,
)
from app.domain.ruleset import get_ruleset

FIXTURE = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "rule_vectors.json"
_data = json.loads(FIXTURE.read_text(encoding="utf-8"))
VECTORS = _data["golden"] + _data["fuzz"]
REASON_MESSAGES = _data["reason_messages"]
RULESET = get_ruleset()


def _to_input(v: dict) -> DecisionInput:
    inp = v["input"]
    mastery = {
        cid: MasteryEntry(p_bp=m["p_bp"], attempts=m.get("attempts", 0),
                          correct=m.get("correct", 0),
                          last_event_seq=m.get("last_event_seq", 0))
        for cid, m in inp["mastery"].items()
    }
    return DecisionInput(
        trigger_event_type=inp["trigger_event_type"],
        trigger_concept_id=inp["trigger_concept_id"],
        trigger_correct=inp["trigger_correct"],
        mastery=mastery,
        recent_events=[
            RecentEvent(seq=e["seq"], event_type=e["event_type"],
                        concept_id=e.get("concept_id"),
                        correct=e.get("correct"),
                        p_bp_after=e.get("p_bp_after"),
                        last_action=e.get("last_action"))
            for e in inp["recent_events"]
        ],
        prereqs=inp["prereqs"],
        concept_order=inp["concept_order"],
        chapter_id_for_concept=inp["chapter_id_for_concept"],
        doubt_concept_hint=inp.get("doubt_concept_hint"),
        env_network=inp["env_network"],
        installed_pack_versions=inp["installed_pack_versions"],
        required_pack_for_concept=inp["required_pack_for_concept"],
        storage_free_mb=inp.get("storage_free_mb", 1_000_000),
        battery_saver=inp.get("battery_saver", False),
        outbox_nonempty=inp.get("outbox_nonempty", False),
        ruleset_version=inp["ruleset_version"],
    )


@pytest.mark.parametrize("vector", VECTORS, ids=[v["name"] for v in VECTORS])
def test_vector(vector) -> None:
    out = decide(_to_input(vector), RULESET, REASON_MESSAGES)
    expected = vector["expected"]
    assert out.action == expected["action"]
    assert out.delivery_mode == expected["delivery_mode"]
    assert out.background_actions == expected["background_actions"]
    assert out.target_concept_id == expected["target_concept_id"]
    assert out.reason_code == expected["reason_code"]
    assert out.needs_help == expected["needs_help"]


@pytest.mark.parametrize("vector", _data["invalid"], ids=[v["name"] for v in _data["invalid"]])
def test_invalid_vector_falls_back(vector) -> None:
    inp = _to_input(vector)
    assert engine_error(inp, RULESET) is not None, "input must be detected invalid"
    out = decide(inp, RULESET, REASON_MESSAGES)
    assert out.reason_code == vector["expected"]["reason_code"]
    assert out.fallback is True
    # The fallback must still be a valid, displayable decision.
    assert out.action in ("REMEDIATE", "RETRY", "REVISE", "ADVANCE")
    assert out.delivery_mode in ("cached", "rich", "prefetch_then_offline")


# --------------------------------------------------------------------------- #
# BKT sequences (Appendix A) — integer arithmetic, half-up rounding, clamps
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("case", _data["bkt"], ids=[c["name"] for c in _data["bkt"]])
def test_bkt_sequence(case) -> None:
    p = case["p_init_bp"]
    for i, step in enumerate(case["steps"]):
        p = bkt_update_bp(p, step["correct"], RULESET)
        assert p == step["p_bp"], f"step {i} diverged"
        assert mastery_band_bp(p, RULESET) == step["band"]
        assert 100 <= p <= 9900, "clamped to [100, 9900]"


def test_round_half_up_div() -> None:
    assert round_half_up_div(5, 2) == 3        # .5 rounds UP
    assert round_half_up_div(3, 2) == 2
    assert round_half_up_div(4, 2) == 2
    assert round_half_up_div(1, 3) == 0
    assert round_half_up_div(2, 3) == 1
    assert round_half_up_div(0, 7) == 0
    with pytest.raises(ValueError):
        round_half_up_div(1, 0)


def test_bkt_replay_is_exact() -> None:
    """Replaying the same accepted answer sequence reproduces the same
    mastery projection exactly (v2 replay invariant)."""
    seq = [(True, False), (False, True), (True, True), (False, False)]
    answers = [correct for correct, _ in seq]
    forward = 2000
    for correct in answers:
        forward = bkt_update_bp(forward, correct, RULESET)
    # Replay from the same start must land on the same integer.
    replay = 2000
    for correct in answers:
        replay = bkt_update_bp(replay, correct, RULESET)
    assert forward == replay
    # Every update starts from the persisted integer: applying the same
    # update twice to a stored value is idempotent in output shape.
    once = bkt_update_bp(2000, True, RULESET)
    assert isinstance(once, int) and 100 <= once <= 9900
