# SAARTHI — Implementation Status

Last updated: Post-Implementation Verification (Design Document v2 Compliance)

This document tracks the verified implementation status across all subsystems of SAARTHI, categorized strictly into three states:
1. **Implemented and Tested** (verified by automated tests in the local environment)
2. **Implemented but Not Adequately Verified** (code exists but requires additional real-world benchmarks or physical hardware testing)
3. **Not Implemented or Blocked by External Dependency** (depends on external cloud credentials, live physical hardware, or third-party human review)

---

## 1. Implemented and Tested

| Requirement / Component | Design Section | Evidence / Verification Test |
|---|---|---|
| **Deterministic Decision Engine (Python)** | Sec 4, 6, App A | 293 passed in pytest (`backend/tests/test_decide_vectors.py`, `test_bloom.py`) |
| **Deterministic Decision Engine (TypeScript)** | Sec 4, 6, App A | 185 passed in vitest (`frontend/tests/decide.test.ts`) |
| **Cross-Language Engine Parity (100%)** | N9, Sec 6.2, 15 | 165 shared rule vectors pass identically in Python and TypeScript |
| **BKT Integer Basis-Point Arithmetic** | Sec 6, App A | Bit-for-bit integer arithmetic (0..10000 bp), half-up rounding in `bkt.py` and `decide.ts` |
| **Bloom's Taxonomy Framework (6 Levels)** | Sec 5.4 | Level hierarchy, transition matrix, prerequisite rules in `bloom.py` and `bloom.ts` |
| **Active-Profile Persistence & Startup** | Sec 4.1 | Startup state machine (`initializing`, `profile_required`, `profile_active`, `storage_unavailable`, `recovery_error`) in `App.tsx` and `profile_session.ts` |
| **Local PIN Verification & Multi-Profile UX** | Sec 4.2, 4.3, 14 | 4-digit PIN setup, validation, PBKDF2 verification, and multi-profile isolation in `ProfilePicker.tsx` |
| **Pack Checksum & Resumable Downloads** | Sec 4.4, 4.5, 10 | HTTP 206 Partial Content range requests, 512 KB chunk resumption, and SHA-256 archive verification in `packs.py` and `pack_downloader.ts` |
| **Answer Grounding & Entailment** | Sec 4.6, 13 | `DeterministicOdiaEntailer` and `validate_answer_full` wired into LangGraph in `graph.py` |
| **Question Bank Expansion (108 Questions)** | Sec 5.1 | Exactly 12 questions/concept across all 9 concepts (4 easy, 4 medium, 4 hard) covering all 6 Bloom levels |
| **Option-Level Misconception Tags** | Sec 5.2 | `QuestionOption` schema, server grading extraction, and Odia misconception feedback in `Lesson.tsx` |
| **Curriculum Chunks Word Count** | Sec 5.3 | All 18 chunks in Ch 1–3 expanded to 89–108 Odia words (well within [80, 200] target) |
| **Strict Publication Gate (100% Pass)** | Sec 5.5 | `scripts/build_packs.py --strict` passes with code 0 on all 3 chapters |
| **Offline Fault Matrix (9 Scenarios)** | Sec 6.6, 15 | `backend/tests/integration/test_offline_fault_matrix.py` (9 passed in 1.39s) |
| **LangGraph Orchestration State Machine** | Sec 4, 5, 7.1 | Compiled `StateGraph` with nodes (`translate`, `retrieve`, `generate`, `validate`) and checkpointer in `graph.py` |
| **Arq Worker & Durable Jobs Table** | Sec 5, 7.2 | Durable `jobs` table in PostgreSQL/SQLite schema, `JobWorker`, reconciler, and admin endpoint `GET /api/v1/admin/jobs` (`test_worker_jobs.py`) |
| **Alembic PostgreSQL Migrations** | Sec 7.3 | Async Alembic migrations `001_initial_schema.py` and `002_add_jobs_and_misconceptions.py` verified to head |
| **Object Storage Adapter (Local + MinIO/S3)** | Sec 7.4 | `LocalObjectStorage` and `S3MinIOStorage` with atomic promotion, range slicing, and SHA-256 verification (`test_storage.py`) |
| **Redis Rate Limiting & Bounded Cache** | Sec 5, 7.5 | Redis sliding window counter with bounded in-memory token bucket fallback in `RateLimitMiddleware` |
| **Database Backup & Restore Replay Drill** | Sec 5, 7.6, 15 | Logical dump, restore-to-scratch, and 100% canonical replay verification in `scripts/db_backup_restore.py` |
| **Background Prefetch Scheduler** | Sec 8.1, 10 | Non-blocking download scheduler checking storage budget (>=150 MB free) and good network in `prefetch_scheduler.ts` |
| **Dedicated Progress Screen** | Sec 8.2, App B | Concept color map, mastery bands, and Odia teacher help prompt in `Progress.tsx` |
| **Decision-Quality Gold Set (120 Scenarios)** | Sec 11.1, 15 | 100% structural validity, 90.5% held-out agreement (target >=90%) verified via `scripts/eval_decision_quality.py` |
| **Odia Retrieval Benchmark (100 Queries)** | Sec 9.1, 11 | 100 labeled Odia queries in `tests/fixtures/odia_queries.jsonl` evaluated via `scripts/eval_retrieval.py` |

---

## 2. Implemented but Not Adequately Verified

| Requirement / Component | Design Section | Reason / Verification Gap |
|---|---|---|
| **Live Multi-learner Load Stress** | Sec 15 | Replay and sync property tests pass locally, but concurrent stress testing with 50+ simulated devices requires staging cluster. |
| **Local Device BM25 Retrieval Latency** | N3, Sec 15 | Verified under 20 ms in Node/V8 environment; requires validation on 2GB reference hardware. |

---

## 3. Not Implemented or Blocked by External Dependency

| Requirement / Component | Design Section | Blocker / Missing Element | Status / Mitigation |
|---|---|---|---|
| **Remote Multilingual Dense Embedding Benchmark** | Sec 9.1, 12 | Requires live Hugging Face Inference API token or GPU runner (`HF_TOKEN` not configured in env). | Local hybrid retriever evaluated; remote model comparison recorded as `BLOCKED_PENDING_CREDENTIALS` (Rule 12). |
| **External LLM Provider Benchmark (GPT-4 / Claude / Llama-3)** | Sec 9.2, 12 | Requires live paid LLM API keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`). | Extractive grounded answer fallback active; remote comparison recorded as blocked. |
| **Native Odia Independent Human Review** | Sec 9.3, 15 (Gate R3) | Requires independent native Odia reviewers not involved in rule authoring. | Curriculum authored and validated against BSE syllabus; external human sign-off pending. |
| **Online Voice (ASR / TTS)** | Sec 9.4, 12 (P1) | P1 scope; deferred per design decision D-010/D10 until text core passes all gates. | Text-first input/output active. |
| **Physical Reference Device Hardware Measurements** | Sec 11.3, 15 (Gate R5) | Physical 2GB RAM Android phone not connected to this Linux build runner. | Test protocol and measurement instructions documented in `docs/devices.md`. |
| **Real-Student Children's Data Pilot** | Sec 10.1, 14 (Gate R1) | Requires institutional ethics approval and school board consent. | Seeded data and pseudonymous UUIDs only; zero minor PII collected. |
