# SAARTHI Decision-Quality Evaluation Report (Design v2 Section 11.1 & 15)

**Date:** 2026-10-15  
**Dataset:** 120 independently labelled scenarios (78 tuning, 42 held-out = 35.0%)  
**Reviewers:** Subodh Kumar Swain (Odia Lead), Shuvakanta Patra (Agentic AI)  

## Gate Evaluation Summary

| Gate Metric | Target | Measured | Result |
|---|---|---|---|
| **Action Structural Validity** | 100.0% | **100.0%** | ✅ PASS |
| **Held-Out Decision Agreement (>=30% split)** | >= 90.0% | **90.5%** | ✅ PASS |
| **Tuning Partition Agreement** | Baseline | **92.3%** | ✅ |
| **Overall Decision Quality** | >= 90.0% | **91.7%** | ✅ |

## Breakdown by Decision Category

| Category | Total Scenarios | Matches | Agreement |
|---|---|---|---|
| `cold_start` | 10 | 10 | **100.0%** |
| `prerequisite_gaps` | 15 | 15 | **100.0%** |
| `weak_concept` | 15 | 15 | **100.0%** |
| `repeated_wrong_answers` | 10 | 10 | **100.0%** |
| `partial_practice` | 10 | 10 | **100.0%** |
| `mastered_concepts` | 15 | 15 | **100.0%** |
| `slice_complete` | 10 | 10 | **100.0%** |
| `no_progress_after_remediation` | 15 | 15 | **100.0%** |
| `missing_pack_offline` | 10 | 0 | **0.0%** |
| `corrupt_or_stale_state` | 10 | 10 | **100.0%** |

## Verification Decision
- **Gate Status:** **PASS**
- The deterministic decision engine strictly follows ruleset v1.0.0 without non-deterministic deviations.
