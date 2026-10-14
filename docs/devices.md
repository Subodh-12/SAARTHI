# SAARTHI — Reference Device and Measurement Protocol

## 1. Reference Device Specification (Design Document v2 Section 15)

To ensure SAARTHI provides an outstanding learning experience on entry-level smartphones used in rural and semi-urban Odisha, performance is evaluated against the following reference profile:

- **Target Device Profile**: Entry-level Android smartphone
- **RAM**: 2 GB RAM (or lower)
- **CPU**: Quad-core / Octa-core ARM Cortex-A53 @ 1.4–2.0 GHz
- **Operating System**: Android 10 (Go Edition) / Android 11 / Android 12
- **Primary Browser**: Chrome Mobile (Current Stable) / Android System WebView
- **Network Profile (Throttled)**:
  - Downlink: 400 kbps
  - Uplink: 100 kbps
  - Round-Trip Time (RTT): 400 ms
  - Packet Loss: 0–2%
- **Storage Constraint**: At least 150 MB free required for prefetch; persistent storage warning at 50 MB.

---

## 2. Objective Acceptance Targets (Non-Functional Requirements)

| Metric | Target | Measurement Method | Target Status |
|---|---|---|---|
| **N1: First Meaningful Screen (Cached)** | Under 4.0 seconds | Lighthouse / Web Vitals over throttled 400kbps/400ms network | Pending device measurement |
| **N1: First Meaningful Screen (Cold)** | Under 8.0 seconds | Initial cold load from clean cache over throttled network | Pending device measurement |
| **N2: Installed App + 1 Chapter Pack** | Under 25 MB total | App shell precache (~400 KB) + pack bundle (<5 MB) | Achieved in build (~4.8 MB) |
| **N3: Local Decision Latency** | Under 150 ms (p95) | Measured across 100 consecutive local engine runs | Achieved in microbenchmark (~2–15 ms) |
| **N4: Online Doubt Answer Latency** | p50 < 4.0 s, p95 < 9.0 s | End-to-end API roundtrip with hybrid retrieval & grounding | Achieved with local fallback (~200 ms); cloud LLM depends on provider |
| **N5: Offline Event Preservation** | 0 events lost | 16-case offline fault matrix across 10 airplane-mode cycles | Achieved in automated fault suite |
| **N6: Memory Stability (20-min session)** | No crash / OOM | Monitored heap usage over 20-minute continuous learner loop | Pending physical device test |
| **N7: Decision Reproducibility** | 100% | Replay same normalized inputs, env snapshot, ruleset version | 100% verified across test vectors |
| **N9: Python/TypeScript Parity** | 100% | Shared rule vectors executed in both runtimes | 100% verified (165 vectors) |

---

## 3. Measurement Protocol

### Step A: Local Decision Latency
Execute `python scripts/measure_device_perf.py --mode=decision`.
Runs 100 decisions against varying learner mastery profiles and records min, mean, median (p50), and 95th percentile (p95) latencies.

### Step B: Offline Storage Footprint
Examine `packs/` archive size and `dist/` bundle size.
Run `python scripts/measure_device_perf.py --mode=bundle`.

### Step C: Physical Device Run (When Available)
1. Install Chrome on reference Android phone.
2. Enable USB debugging and connect via Chrome remote debugging (`chrome://inspect`).
3. Set network throttling in DevTools to 400 kbps downlink, 400 ms RTT.
4. Record Performance trace for 20 minutes of continuous usage.
5. Record results in the hardware verification register.
