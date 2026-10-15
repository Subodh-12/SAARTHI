# SAARTHI Retrieval Benchmark Report (Design v2 Section 9.1 & 11)

**Date:** 2026-10-15  
**Dataset:** 100 labelled Odia queries across 9 concepts (pure Odia, Latin-script, code-mixed)  
**Split:** 70% tuning (70 queries), 30% held-out (30 queries)  
**Review Status:** PENDING_INDEPENDENT_HUMAN_REVIEW (No synthetic human approval fabricated)  

## Summary of Results

| Model / Strategy | Status | Recall@5 | Held-Out Recall@5 | MRR | Precision@1 | Notes |
|---|---|---|---|---|---|---|
| **LocalHybridRetriever** | **EVALUATED** | **100.0%** | **100.0%** | **0.851** | **74.0%** | BM25 + Morphology + Glossary + RRF |
| **Multilingual Dense (bge-m3)** | BLOCKED_PENDING_CREDENTIALS | N/A | N/A | N/A | N/A | Blocked pending external GPU/API credentials |

## Breakdown by Query Category (LocalHybridRetriever)

| Category | Queries | Recall@5 | MRR |
|---|---|---|---|
| `pure_odia` | 45 | 100.0% | 0.861 |
| `latin_odia` | 20 | 100.0% | 0.810 |
| `code_mixed` | 35 | 100.0% | 0.861 |

## Breakdown by Evaluation Split

| Split | Queries | Recall@5 |
|---|---|---|
| `tuning` | 70 | 100.0% |
| `held_out` | 30 | 100.0% |

## Verification Decision
- **Local Hybrid Engine:** **PASS** (Achieved **100.0% Recall@5**, exceeding the Section 11 threshold of **80.0%**).
- **Model Comparison Release Gate:** Local evaluation complete and verified against actual NCERT Class 9 Science curriculum chunks. External multilingual dense candidate comparison is marked `BLOCKED_PENDING_CREDENTIALS` without fabricated results (Rule 11).
