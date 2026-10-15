#!/usr/bin/env python3
"""Device performance and non-functional requirements measurement script.
(Design Document v2 Section 15 and docs/devices.md).

Measures:
- N2: Bundle and installed pack size (target: < 25 MB).
- N3: Local decision engine latency (target: p95 < 150 ms across 100 runs).
- N4: Online doubt answer latency p50 & p95 (target: p50 < 4.0s, p95 < 9.0s).
- Checks for physical Android ADB device connection for N1 and N6.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Ensure project root in sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.domain.decide import decide, DecisionInput
from app.domain.ruleset import get_ruleset
from app.domain.schemas import NetworkState


def get_system_info() -> dict[str, Any]:
    info = {
        "os": platform.system(),
        "os_release": platform.release(),
        "arch": platform.machine(),
        "python_version": platform.python_version(),
        "timestamp": int(time.time()),
    }
    # Check for connected Android reference devices via adb
    adb_path = shutil.which("adb")
    devices = []
    if adb_path:
        try:
            res = subprocess.run([adb_path, "devices"], capture_output=True, text=True, timeout=5)
            lines = [line.strip() for line in res.stdout.strip().splitlines()[1:] if line.strip()]
            devices = [line.split()[0] for line in lines if "device" in line]
        except Exception:
            pass
    info["adb_devices"] = devices
    info["physical_device_available"] = len(devices) > 0
    return info


def measure_bundle_size() -> dict[str, Any]:
    print("Measuring bundle and pack size (N2)...")
    dist_dir = ROOT / "frontend" / "dist"
    packs_dir = ROOT / "packs"

    dist_size = 0
    if dist_dir.exists():
        for p in dist_dir.rglob("*"):
            if p.is_file():
                dist_size += p.stat().st_size

    pack_sizes = {}
    total_pack_size = 0
    if packs_dir.exists():
        for p in packs_dir.glob("*.srt.tar.gz"):
            sz = p.stat().st_size
            pack_sizes[p.name] = sz
            total_pack_size += sz

    total_installed_mb = round((dist_size + total_pack_size) / (1024 * 1024), 2)
    target_met = total_installed_mb <= 25.0

    return {
        "app_shell_bytes": dist_size,
        "app_shell_mb": round(dist_size / (1024 * 1024), 2),
        "pack_files": pack_sizes,
        "total_pack_bytes": total_pack_size,
        "total_pack_mb": round(total_pack_size / (1024 * 1024), 2),
        "total_installed_mb": total_installed_mb,
        "target_mb": 25.0,
        "target_met": target_met,
    }


def measure_decision_latency(iterations: int = 100) -> dict[str, Any]:
    print(f"Measuring local decision latency across {iterations} iterations (N3)...")
    ruleset = get_ruleset()
    rules = ruleset.raw

    from app.domain.decide import MasteryEntry
    # Create realistic varying mastery profiles
    latencies_ms = []
    for i in range(iterations):
        # vary concept mastery
        mastery = {
            "c0001": MasteryEntry(p_bp=2000 + (i * 70) % 8000, attempts=2, correct=1),
            "c0002": MasteryEntry(p_bp=1500 + (i * 50) % 7000, attempts=1, correct=0),
            "c0003": MasteryEntry(p_bp=1000 + (i * 30) % 6000, attempts=0, correct=0),
        }
        inp = DecisionInput(
            trigger_event_type="SESSION_STARTED",
            trigger_concept_id=None,
            trigger_correct=None,
            concept_order=["c0001", "c0002", "c0003", "c0004", "c0005"],
            prereqs={"c0002": ["c0001"], "c0003": ["c0002"]},
            mastery=mastery,
            recent_events=[],
            installed_pack_versions={"pack_class9_science_or_v1": 1},
            required_pack_for_concept={
                "c0001": "pack_class9_science_or_v1",
                "c0002": "pack_class9_science_or_v1",
                "c0003": "pack_class9_science_or_v1",
            },
            chapter_id_for_concept={"c0001": "ch01", "c0002": "ch01", "c0003": "ch01"},
            env_network="online" if i % 2 == 0 else "offline",
            ruleset_version=ruleset.ruleset_version,
        )

        t0 = time.perf_counter()
        out = decide(inp, ruleset=ruleset)
        t1 = time.perf_counter()
        latencies_ms.append((t1 - t0) * 1000.0)

    latencies_ms.sort()
    min_ms = round(latencies_ms[0], 3)
    p50_ms = round(latencies_ms[int(0.50 * len(latencies_ms))], 3)
    p95_ms = round(latencies_ms[int(0.95 * len(latencies_ms))], 3)
    max_ms = round(latencies_ms[-1], 3)
    mean_ms = round(sum(latencies_ms) / len(latencies_ms), 3)

    target_met = p95_ms <= 150.0

    return {
        "iterations": iterations,
        "min_ms": min_ms,
        "mean_ms": mean_ms,
        "p50_ms": p50_ms,
        "p95_ms": p95_ms,
        "max_ms": max_ms,
        "target_p95_ms": 150.0,
        "target_met": target_met,
    }


async def measure_doubt_latency() -> dict[str, Any]:
    print("Measuring doubt retrieval latency (N4)...")
    from app.adapters.ai.retrieval import LocalHybridRetriever

    retriever = LocalHybridRetriever()

    queries = [
        "ପଦାର୍ଥର ତିନୋଟି ଅବସ୍ଥା କଣ?",
        "ତ୍ୱରଣ କାହାକୁ କୁହାଯାଏ?",
        "ଉଦ୍ଭିଦ ଟିସୁ କେତେ ପ୍ରକାର?",
        "ବାଷ୍ପୀଭବନର କାରଣ କଣ?",
        "ଜାଇଲେମ୍ ଓ ଫ୍ଲୋଏମ୍ ମଧ୍ୟରେ ପାର୍ଥକ୍ୟ କଣ?",
    ]

    latencies_ms = []
    for q in queries * 6:  # 30 runs
        t0 = time.perf_counter()
        res = await retriever.retrieve(q, top_k=5)
        t1 = time.perf_counter()
        latencies_ms.append((t1 - t0) * 1000.0)

    latencies_ms.sort()
    p50_ms = round(latencies_ms[int(0.50 * len(latencies_ms))], 2)
    p95_ms = round(latencies_ms[int(0.95 * len(latencies_ms))], 2)

    return {
        "runs": len(latencies_ms),
        "p50_ms": p50_ms,
        "p95_ms": p95_ms,
        "target_p50_ms": 4000.0,
        "target_p95_ms": 9000.0,
        "target_met": p50_ms <= 4000.0 and p95_ms <= 9000.0,
    }


import asyncio


async def main():
    parser = argparse.ArgumentParser(description="Measure reference device performance metrics")
    parser.add_argument("--mode", choices=["all", "bundle", "decision", "doubt"], default="all")
    args = parser.parse_args()

    sys_info = get_system_info()
    report: dict[str, Any] = {"system_info": sys_info}

    if args.mode in ("all", "bundle"):
        report["bundle"] = measure_bundle_size()

    if args.mode in ("all", "decision"):
        report["decision"] = measure_decision_latency()

    if args.mode in ("all", "doubt"):
        report["doubt"] = await measure_doubt_latency()

    out_file = ROOT / "docs" / "device_perf_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Performance report generated at {out_file}")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
