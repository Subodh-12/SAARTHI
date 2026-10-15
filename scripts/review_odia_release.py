#!/usr/bin/env python3
"""Native Odia human-review workflow and release report generator.
(Design Document v2 Section 12 & Section 15).

Dimensions evaluated (scored 1 to 5 by native reviewer):
1. Correctness against cited chunk: Facts match source (Target: >=4 on 90% of samples)
2. Fluency: Reads as natural Odia (Target: >=4 on 90% of samples)
3. Register: Right level for Class 9 (Target: >=4 on 90% of samples)
4. Terminology: Glossary terms used consistently (Target: 95% of terms correct)

Honesty requirement:
If independent human reviews have not yet been completed by a qualified native speaker,
the release gate MUST be marked BLOCKED_PENDING_INDEPENDENT_HUMAN_REVIEW rather than
substituting synthetic approvals.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parent.parent
REVIEW_DATA_FILE = ROOT / "tests" / "fixtures" / "odia_human_reviews.json"
REPORT_MD = ROOT / "docs" / "native_odia_review_report.md"
REPORT_JSON = ROOT / "docs" / "native_odia_review_report.json"


def load_reviews() -> list[dict[str, Any]]:
    if not REVIEW_DATA_FILE.exists():
        return []
    try:
        data = json.loads(REVIEW_DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def generate_report(reviews: list[dict[str, Any]]) -> dict[str, Any]:
    total_reviews = len(reviews)
    valid_human_reviews = [r for r in reviews if r.get("reviewer_type") == "human_native_speaker" and r.get("verified")]

    if not valid_human_reviews:
        status = "BLOCKED_PENDING_INDEPENDENT_HUMAN_REVIEW"
        summary = {
            "status": status,
            "total_reviews": total_reviews,
            "verified_human_reviews": 0,
            "required_samples": 50,
            "correctness_pass_rate": None,
            "fluency_pass_rate": None,
            "register_pass_rate": None,
            "terminology_pass_rate": None,
            "blocker_description": "Gate pending independent human review by a native Odia speaker according to Design Document v2 Section 12.",
        }
    else:
        # Calculate statistics
        c_pass = sum(1 for r in valid_human_reviews if r.get("scores", {}).get("correctness", 0) >= 4)
        f_pass = sum(1 for r in valid_human_reviews if r.get("scores", {}).get("fluency", 0) >= 4)
        r_pass = sum(1 for r in valid_human_reviews if r.get("scores", {}).get("register", 0) >= 4)
        t_pass = sum(1 for r in valid_human_reviews if r.get("scores", {}).get("terminology", 0) >= 4)
        n = len(valid_human_reviews)

        c_rate = round(c_pass / n, 4)
        f_rate = round(f_pass / n, 4)
        r_rate = round(r_pass / n, 4)
        t_rate = round(t_pass / n, 4)

        gate_pass = n >= 50 and c_rate >= 0.90 and f_rate >= 0.90 and r_rate >= 0.90 and t_rate >= 0.95
        status = "PASS" if gate_pass else "FAIL"

        summary = {
            "status": status,
            "total_reviews": total_reviews,
            "verified_human_reviews": n,
            "required_samples": 50,
            "correctness_pass_rate": c_rate,
            "fluency_pass_rate": f_rate,
            "register_pass_rate": r_rate,
            "terminology_pass_rate": t_rate,
            "blocker_description": None if gate_pass else "Pass rate thresholds or minimum sample count (50) not met.",
        }

    report = {
        "report_date": "2026-10-15",
        "gate_name": "R3: Native Odia Quality Review Gate",
        "design_reference": "Design Document v2 Section 12 & Section 15",
        "summary": summary,
        "rubric": {
            "correctness": "Score 1-5; Facts match cited chunk (Target >= 4 on 90%)",
            "fluency": "Score 1-5; Reads as natural Odia (Target >= 4 on 90%)",
            "register": "Score 1-5; Right level for Class 9 (Target >= 4 on 90%)",
            "terminology": "Glossary terms used consistently (Target >= 95%)",
        },
        "reviews": reviews,
    }

    # Write JSON report
    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Write Markdown report
    md_content = f"""# SAARTHI — Native Odia Review Release Gate Report

**Date**: {report['report_date']}  
**Status**: `{summary['status']}`  
**Reference**: Design Document v2 Section 12 & 15  

## Rubric and Targets
- **Correctness against cited chunk**: Facts match source (Target: >=4 on 90% of samples)
- **Fluency**: Reads as natural Odia (Target: >=4 on 90% of samples)
- **Register**: Right level for Class 9 (Target: >=4 on 90% of samples)
- **Terminology**: Glossary terms used consistently (Target: 95% of terms correct)

## Verification Status
- **Verified Native Human Reviews Logged**: {summary['verified_human_reviews']} / {summary['required_samples']}
- **Gate Evaluation**: `{summary['status']}`

"""
    if summary["blocker_description"]:
        md_content += f"> [!IMPORTANT]\n> **Release Blocker (R3)**: {summary['blocker_description']}\n> Synthetic reviewer approvals or automated LLM self-evaluations must not be substituted for native human sign-off.\n"

    REPORT_MD.write_text(md_content, encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description="Generate Native Odia Human Review Gate Report")
    parser.parse_args()

    reviews = load_reviews()
    report = generate_report(reviews)

    print(f"Report generated: {REPORT_JSON}")
    print(f"Status: {report['summary']['status']}")


if __name__ == "__main__":
    main()
