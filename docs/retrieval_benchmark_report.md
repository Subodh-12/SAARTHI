# SAARTHI Retrieval Benchmark Report (Design v2 Section 9.1 & 11)

**Date:** 2026-10-15  
**Dataset:** 100 labelled Odia queries across 9 concepts (pure Odia, Latin-script, code-mixed)  
**Reviewer:** Subodh Kumar Swain (Odia Lead) (APPROVED)  

## Summary of Results

| Model / Strategy | Status | Recall@5 | MRR | Precision@1 | Notes |
|---|---|---|---|---|---|
| **LocalHybridRetriever** | EVALUATED | **25.0%** | **0.117** | **6.0%** | BM25 + Glossary Expansion |
| **Multilingual Dense** | BLOCKED_PENDING_CREDENTIALS | N/A | N/A | N/A | Blocked pending external GPU/API credentials |

## Breakdown by Query Category (LocalHybridRetriever)

| Category | Queries | Recall@5 | MRR |
|---|---|---|---|
| `pure_odia` | 47 | 34.0% | 0.162 |
| `latin_odia` | 12 | 16.7% | 0.125 |
| `code_mixed` | 41 | 17.1% | 0.063 |

## Verification Decision
- **Local Hybrid Engine:** Meets baseline requirements for offline & server retrieval.
- **Model Comparison Release Gate:** Local evaluation complete. External dense comparison is recorded as `BLOCKED_PENDING_CREDENTIALS` without fabricated results (Rule 12).
