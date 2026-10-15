# SAARTHI Decision-Quality Evaluation Report (Design v2 Section 11.1 & 15)

**Date:** 2026-10-15  
**Dataset:** 120 scenarios (78 tuning, 42 held-out = 35.0%)  
**Dataset Type:** `provisional_mechanical_corpus` (Mechanically derived rule coverage corpus. Independent human panel review pending.)  
**Independent Human Reviewed:** ⚠️ PENDING (Provisional Mechanical Corpus)  

## Gate Evaluation Summary

| Gate Metric | Target | Measured | Result |
|---|---|---|---|
| **Action Structural Validity** | 100.0% | **100.0%** | ✅ PASS |
| **Held-Out Decision Agreement (>=30% split)** | >= 90.0% | **100.0%** | ✅ PASS |
| **Tuning Partition Agreement** | Baseline | **100.0%** | ✅ |
| **Overall Decision Quality** | >= 90.0% | **100.0%** | ✅ PASS |
| **Target Concept Validity** | >= 90.0% | **100.0%** | ✅ PASS |
| **Delivery Mode Validity** | >= 90.0% | **100.0%** | ✅ PASS |
| **Reason Code Agreement** | >= 90.0% | **100.0%** | ✅ PASS |
| **Background Action Agreement** | >= 90.0% | **100.0%** | ✅ PASS |
| **Category Gates (All >= 90%)** | 0 failures | **0 failures** | ✅ PASS |
| **Python / TypeScript Parity** | 100% | **Verified via rule vectors** | ✅ PASS |

## Breakdown by Decision Category

| Category | Total Scenarios | Matches | Agreement | Gate Status |
|---|---|---|---|---|
| `cold_start` | 10 | 10 | **100.0%** | ✅ PASS |
| `prerequisite_gaps` | 15 | 15 | **100.0%** | ✅ PASS |
| `weak_concept` | 15 | 15 | **100.0%** | ✅ PASS |
| `repeated_wrong_answers` | 10 | 10 | **100.0%** | ✅ PASS |
| `partial_practice` | 10 | 10 | **100.0%** | ✅ PASS |
| `mastered_concepts` | 15 | 15 | **100.0%** | ✅ PASS |
| `slice_complete` | 10 | 10 | **100.0%** | ✅ PASS |
| `no_progress_after_remediation` | 15 | 15 | **100.0%** | ✅ PASS |
| `missing_pack_offline` | 10 | 10 | **100.0%** | ✅ PASS |
| `corrupt_or_stale_state` | 10 | 10 | **100.0%** | ✅ PASS |

## Verification Decision
- **Gate Status:** **PASS**
- **Notes:** All categories and structural gates passed.
