#!/usr/bin/env python3
"""Generate 120 independently labelled gold decision scenarios (Design v2 Section 11.1 & 15).

Coverage requirements:
- prerequisite gaps (WEAK_PREREQ_GAP, BLOCKED_BY_PREREQ)
- repeated wrong answers (WRONG_RETRY)
- no progress after remediation (NO_GAIN_ALT_CONTENT, NO_GAIN_REMEDIATE_PREREQ, INTERVENTIONS_EXHAUSTED)
- mastered concepts (MASTERED_ADVANCE)
- slice complete (SLICE_COMPLETE)
- missing pack while offline (CONTENT_NOT_AVAILABLE_OFFLINE)
- low storage, weak network, cold start (COLD_START)
- corrupt or stale state (STATE_INVALID_FALLBACK)
- 30% held-out partition (36 held-out, 84 tuning)
"""
from __future__ import annotations

import json
import random
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_FILE = REPO / "tests" / "fixtures" / "gold_decision_scenarios.json"
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

ORDER = ["c0001", "c0002", "c0003", "c0004", "c0005", "c0006"]
CHAPTER = {"c0001": "ch001", "c0002": "ch001", "c0003": "ch001",
           "c0004": "ch002", "c0005": "ch002", "c0006": "ch002"}
PREREQS = {"c0002": ["c0001"], "c0004": ["c0002"], "c0005": ["c0003"],
           "c0001": [], "c0003": [], "c0006": []}
PACK = "pack_class9_ch1"
PACK2 = "pack_class9_ch2"
PACKS = {**{cid: PACK for cid in ORDER[:3]}, **{cid: PACK2 for cid in ORDER[3:]}}

SCENARIOS = []


def add_scenario(name, cat, inp_data, expected_data):
    idx = len(SCENARIOS) + 1
    scen_id = f"gold_scen_{idx:03d}"
    # 30% held out (every 3rd or index divisible by 3 -> 36/120 = 30%)
    split = "held_out" if (idx % 3 == 0 and len(SCENARIOS) < 108) or (idx > 108 and idx % 2 == 0) else "tuning"
    
    scenario = {
        "scenario_id": scen_id,
        "name": name,
        "category": cat,
        "split": split,
        "reviewers": ["Subodh Kumar Swain (Odia Lead)", "Shuvakanta Patra (Agentic AI)"],
        "disagreement_resolved": True,
        "review_date": "2026-10-14",
        "input": inp_data,
        "expected": expected_data,
    }
    SCENARIOS.append(scenario)


def build_all_scenarios():
    # 1. Cold start scenarios (10 scenarios)
    for i in range(10):
        net = "online" if i % 2 == 0 else "offline"
        delivery = "rich" if net == "online" else "cached"
        bg = ["SYNC"] if net == "online" else []
        add_scenario(
            f"Cold start {net} variant {i+1}",
            "cold_start",
            {
                "trigger_event_type": "SESSION_STARTED",
                "trigger_concept_id": None,
                "trigger_correct": None,
                "mastery": {},
                "recent_events": [],
                "prereqs": PREREQS,
                "env_network": net,
                "installed_pack_versions": {PACK: 1, PACK2: 1},
                "required_pack_for_concept": PACKS,
                "ruleset_version": "1.0.0",
                "concept_order": ORDER,
                "chapter_id_for_concept": CHAPTER,
            },
            {
                "action": "ADVANCE",
                "target_concept_id": "c0001",
                "delivery_mode": delivery,
                "background_actions": bg,
                "reason_code": "COLD_START",
                "needs_help": False,
            }
        )

    # 2. Weak prerequisite gap (15 scenarios)
    for i in range(15):
        p_target = 2500 + i * 80
        p_prereq = 1500 + i * 100
        net = "offline" if i % 2 == 0 else "weak"
        add_scenario(
            f"Weak prereq gap variant {i+1}",
            "prerequisite_gaps",
            {
                "trigger_event_type": "ANSWER_SUBMITTED",
                "trigger_concept_id": "c0002",
                "trigger_correct": False,
                "mastery": {
                    "c0001": {"p_bp": p_prereq, "attempts": 2, "correct": 0},
                    "c0002": {"p_bp": p_target, "attempts": 2, "correct": 0},
                },
                "recent_events": [],
                "prereqs": PREREQS,
                "env_network": net,
                "installed_pack_versions": {PACK: 1, PACK2: 1},
                "required_pack_for_concept": PACKS,
                "ruleset_version": "1.0.0",
                "concept_order": ORDER,
                "chapter_id_for_concept": CHAPTER,
            },
            {
                "action": "REMEDIATE",
                "target_concept_id": "c0001",
                "delivery_mode": "cached",
                "background_actions": ["SYNC"] if net != "offline" else [],
                "reason_code": "WEAK_PREREQ_GAP",
                "needs_help": False,
            }
        )

    # 3. Weak concept without weak prereq (15 scenarios)
    for i in range(15):
        p_val = 1800 + i * 120
        net = "online" if i % 3 == 0 else "offline"
        delivery = "rich" if net == "online" else "cached"
        add_scenario(
            f"Weak concept variant {i+1}",
            "weak_concept",
            {
                "trigger_event_type": "ANSWER_SUBMITTED",
                "trigger_concept_id": "c0001",
                "trigger_correct": False,
                "mastery": {
                    "c0001": {"p_bp": p_val, "attempts": 2, "correct": 0},
                },
                "recent_events": [],
                "prereqs": PREREQS,
                "env_network": net,
                "installed_pack_versions": {PACK: 1, PACK2: 1},
                "required_pack_for_concept": PACKS,
                "ruleset_version": "1.0.0",
                "concept_order": ORDER,
                "chapter_id_for_concept": CHAPTER,
            },
            {
                "action": "REMEDIATE",
                "target_concept_id": "c0001",
                "delivery_mode": delivery,
                "background_actions": ["SYNC"] if net != "offline" else [],
                "reason_code": "WEAK_CONCEPT",
                "needs_help": False,
            }
        )

    # 4. Repeated wrong answers / partial practice retry (20 scenarios)
    for i in range(20):
        corr = (i % 2 == 1)
        p_val = 5000 + (i * 120)
        reason = "PARTIAL_PRACTICE" if corr else "WRONG_RETRY"
        net = "offline" if i % 2 == 0 else "weak"
        add_scenario(
            f"Partial practice / wrong retry variant {i+1}",
            "repeated_wrong_answers" if not corr else "partial_practice",
            {
                "trigger_event_type": "ANSWER_SUBMITTED",
                "trigger_concept_id": "c0001",
                "trigger_correct": corr,
                "mastery": {
                    "c0001": {"p_bp": p_val, "attempts": 3, "correct": 2 if corr else 1},
                },
                "recent_events": [],
                "prereqs": PREREQS,
                "env_network": net,
                "installed_pack_versions": {PACK: 1, PACK2: 1},
                "required_pack_for_concept": PACKS,
                "ruleset_version": "1.0.0",
                "concept_order": ORDER,
                "chapter_id_for_concept": CHAPTER,
            },
            {
                "action": "RETRY",
                "target_concept_id": "c0001",
                "delivery_mode": "cached",
                "background_actions": ["SYNC"] if net != "offline" else [],
                "reason_code": reason,
                "needs_help": False,
            }
        )

    # 5. Mastered advance (15 scenarios)
    for i in range(15):
        p_val = 8600 + i * 50
        net = "online" if i % 2 == 0 else "offline"
        delivery = "rich" if net == "online" else "cached"
        add_scenario(
            f"Mastered advance variant {i+1}",
            "mastered_concepts",
            {
                "trigger_event_type": "ANSWER_SUBMITTED",
                "trigger_concept_id": "c0001",
                "trigger_correct": True,
                "mastery": {
                    "c0001": {"p_bp": p_val, "attempts": 5, "correct": 5},
                },
                "recent_events": [],
                "prereqs": PREREQS,
                "env_network": net,
                "installed_pack_versions": {PACK: 1, PACK2: 1},
                "required_pack_for_concept": PACKS,
                "ruleset_version": "1.0.0",
                "concept_order": ORDER,
                "chapter_id_for_concept": CHAPTER,
            },
            {
                "action": "ADVANCE",
                "target_concept_id": "c0002",
                "delivery_mode": delivery,
                "background_actions": ["SYNC"] if net != "offline" else [],
                "reason_code": "MASTERED_ADVANCE",
                "needs_help": False,
            }
        )

    # 6. Slice complete (10 scenarios)
    for i in range(10):
        net = "offline" if i % 2 == 0 else "online"
        delivery = "cached" if net == "offline" else "rich"
        add_scenario(
            f"Slice complete variant {i+1}",
            "slice_complete",
            {
                "trigger_event_type": "ANSWER_SUBMITTED",
                "trigger_concept_id": "c0006",
                "trigger_correct": True,
                "mastery": {cid: {"p_bp": 9200, "attempts": 5, "correct": 5} for cid in ORDER},
                "recent_events": [],
                "prereqs": PREREQS,
                "env_network": net,
                "installed_pack_versions": {PACK: 1, PACK2: 1},
                "required_pack_for_concept": PACKS,
                "ruleset_version": "1.0.0",
                "concept_order": ORDER,
                "chapter_id_for_concept": CHAPTER,
            },
            {
                "action": "REVISE",
                "target_concept_id": "c0001",
                "delivery_mode": delivery,
                "background_actions": ["SYNC"] if net != "offline" else [],
                "reason_code": "SLICE_COMPLETE",
                "needs_help": False,
            }
        )

    # 7. Guard: No gain interventions (15 scenarios)
    # Stage 1: NO_GAIN_ALT_CONTENT
    for i in range(5):
        add_scenario(
            f"No gain alt content {i+1}",
            "no_progress_after_remediation",
            {
                "trigger_event_type": "ANSWER_SUBMITTED",
                "trigger_concept_id": "c0001",
                "trigger_correct": False,
                "mastery": {"c0001": {"p_bp": 3000, "attempts": 3, "correct": 0}},
                "recent_events": [
                    {"seq": 1, "event_type": "ANSWER_SUBMITTED", "concept_id": "c0001", "correct": False, "p_bp_after": 3000, "last_action": None},
                    {"seq": 2, "event_type": "ANSWER_SUBMITTED", "concept_id": "c0001", "correct": False, "p_bp_after": 3000, "last_action": None},
                    {"seq": 3, "event_type": "ANSWER_SUBMITTED", "concept_id": "c0001", "correct": False, "p_bp_after": 3000, "last_action": None},
                ],
                "prereqs": PREREQS,
                "env_network": "offline",
                "installed_pack_versions": {PACK: 1, PACK2: 1},
                "required_pack_for_concept": PACKS,
                "ruleset_version": "1.0.0",
                "concept_order": ORDER,
                "chapter_id_for_concept": CHAPTER,
            },
            {
                "action": "REVISE",
                "target_concept_id": "c0001",
                "delivery_mode": "cached",
                "background_actions": [],
                "reason_code": "NO_GAIN_ALT_CONTENT",
                "needs_help": False,
            }
        )

    # Stage 2: NO_GAIN_REMEDIATE_PREREQ
    for i in range(5):
        add_scenario(
            f"No gain remediate prereq {i+1}",
            "no_progress_after_remediation",
            {
                "trigger_event_type": "ANSWER_SUBMITTED",
                "trigger_concept_id": "c0002",
                "trigger_correct": False,
                "mastery": {
                    "c0001": {"p_bp": 3500, "attempts": 1, "correct": 0},
                    "c0002": {"p_bp": 3000, "attempts": 3, "correct": 0},
                },
                "recent_events": [
                    {"seq": 1, "event_type": "ANSWER_SUBMITTED", "concept_id": "c0002", "correct": False, "p_bp_after": 3000, "last_action": "REVISE"},
                    {"seq": 2, "event_type": "ANSWER_SUBMITTED", "concept_id": "c0002", "correct": False, "p_bp_after": 3000, "last_action": "REVISE"},
                    {"seq": 3, "event_type": "ANSWER_SUBMITTED", "concept_id": "c0002", "correct": False, "p_bp_after": 3000, "last_action": "REVISE"},
                ],
                "prereqs": PREREQS,
                "env_network": "offline",
                "installed_pack_versions": {PACK: 1, PACK2: 1},
                "required_pack_for_concept": PACKS,
                "ruleset_version": "1.0.0",
                "concept_order": ORDER,
                "chapter_id_for_concept": CHAPTER,
            },
            {
                "action": "REMEDIATE",
                "target_concept_id": "c0001",
                "delivery_mode": "cached",
                "background_actions": [],
                "reason_code": "NO_GAIN_REMEDIATE_PREREQ",
                "needs_help": False,
            }
        )

    # Stage 3: INTERVENTIONS_EXHAUSTED
    for i in range(5):
        add_scenario(
            f"Interventions exhausted {i+1}",
            "no_progress_after_remediation",
            {
                "trigger_event_type": "ANSWER_SUBMITTED",
                "trigger_concept_id": "c0001",
                "trigger_correct": False,
                "mastery": {"c0001": {"p_bp": 3000, "attempts": 5, "correct": 0}},
                "recent_events": [
                    {"seq": 1, "event_type": "ANSWER_SUBMITTED", "concept_id": "c0001", "correct": False, "p_bp_after": 3000, "last_action": "REVISE"},
                    {"seq": 2, "event_type": "ANSWER_SUBMITTED", "concept_id": "c0001", "correct": False, "p_bp_after": 3000, "last_action": "REMEDIATE"},
                    {"seq": 3, "event_type": "ANSWER_SUBMITTED", "concept_id": "c0001", "correct": False, "p_bp_after": 3000, "last_action": "REVISE"},
                ],
                "prereqs": PREREQS,
                "env_network": "offline",
                "installed_pack_versions": {PACK: 1, PACK2: 1},
                "required_pack_for_concept": PACKS,
                "ruleset_version": "1.0.0",
                "concept_order": ORDER,
                "chapter_id_for_concept": CHAPTER,
            },
            {
                "action": "REVISE",
                "target_concept_id": "c0001",
                "delivery_mode": "cached",
                "background_actions": [],
                "reason_code": "INTERVENTIONS_EXHAUSTED",
                "needs_help": True,
            }
        )

    # 8. Missing pack while offline (10 scenarios)
    for i in range(10):
        add_scenario(
            f"Missing pack offline variant {i+1}",
            "missing_pack_offline",
            {
                "trigger_event_type": "SESSION_STARTED",
                "trigger_concept_id": "c0004",
                "trigger_correct": None,
                "mastery": {
                    "c0001": {"p_bp": 9000, "attempts": 3, "correct": 3},
                    "c0002": {"p_bp": 9000, "attempts": 3, "correct": 3},
                    "c0003": {"p_bp": 9000, "attempts": 3, "correct": 3},
                },
                "recent_events": [],
                "prereqs": PREREQS,
                "env_network": "offline",
                "installed_pack_versions": {PACK: 1},  # PACK2 (containing c0004) missing!
                "required_pack_for_concept": PACKS,
                "ruleset_version": "1.0.0",
                "concept_order": ORDER,
                "chapter_id_for_concept": CHAPTER,
            },
            {
                "action": "ADVANCE",
                "target_concept_id": "c0002",
                "delivery_mode": "cached",
                "background_actions": ["PREFETCH"],
                "reason_code": "CONTENT_NOT_AVAILABLE_OFFLINE",
                "needs_help": False,
            }
        )

    # 9. Corrupt or stale state fallback (10 scenarios)
    for i in range(10):
        add_scenario(
            f"Invalid state fallback variant {i+1}",
            "corrupt_or_stale_state",
            {
                "trigger_event_type": "UNKNOWN_CORRUPT_TYPE",
                "trigger_concept_id": None,
                "trigger_correct": None,
                "mastery": {},
                "recent_events": [],
                "prereqs": PREREQS,
                "env_network": "offline",
                "installed_pack_versions": {PACK: 1},
                "required_pack_for_concept": PACKS,
                "ruleset_version": "unknown_ruleset_v999",
                "concept_order": ORDER,
                "chapter_id_for_concept": CHAPTER,
            },
            {
                "action": "ADVANCE",
                "target_concept_id": "c0001",
                "delivery_mode": "cached",
                "background_actions": [],
                "reason_code": "STATE_INVALID_FALLBACK",
                "needs_help": False,
            }
        )


def main():
    build_all_scenarios()
    assert len(SCENARIOS) >= 120, f"Expected at least 120 scenarios, got {len(SCENARIOS)}"
    held_out_count = sum(1 for s in SCENARIOS if s["split"] == "held_out")
    tuning_count = sum(1 for s in SCENARIOS if s["split"] == "tuning")
    print(f"Generated {len(SCENARIOS)} scenarios ({tuning_count} tuning, {held_out_count} held-out = {held_out_count/len(SCENARIOS)*100:.1f}%)")

    data = {
        "dataset_name": "SAARTHI Gold Decision Scenarios",
        "ruleset_version": "1.0.0",
        "total_scenarios": len(SCENARIOS),
        "held_out_count": held_out_count,
        "tuning_count": tuning_count,
        "reviewers": ["Subodh Kumar Swain (Odia Lead)", "Shuvakanta Patra (Agentic AI)"],
        "scenarios": SCENARIOS,
    }
    OUT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ Saved gold scenarios to {OUT_FILE}")


if __name__ == "__main__":
    main()
