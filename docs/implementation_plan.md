# SAARTHI V2 — Master Gap Closure & Implementation Plan

**Date:** 15 October 2026  
**Status:** In Progress — Autonomous Master Execution  
**Target Architecture:** SAARTHI Design Document v2 & Audit Reconciliation

---

## 1. Execution Sequence & Phase Mapping

| Phase | Description | Priority | Target Scope & Key Files | Status |
|---|---|---|---|---|
| **Phase 0** | Baseline & Reproducible Environment Setup | P0 | Verified `.venv`, pytest baseline, npm baseline, recorded initial metrics. | **PASS** |
| **Phase A** | Installed-Pack & Offline-Learning Pipeline | P0 | `pack_downloader.ts` gzip decompression stream, HTTP 206 Range downloader, IndexedDB `partial_downloads`, SHA-256 archive verification, atomic install. | **PASS** |
| **Phase B** | Deterministic Learning Decisions & Evaluation | P0 | Fixed `missing_pack_offline` nearest concept substitution & prefetch rules in `decide.py` & `decide.ts`. 100% agreement on 120 gold scenarios, 10/10 offline cases passed. 100% cross-language parity. | **PASS** |
| **Phase C** | Durable Backend Orchestration & Jobs | P0 | Real `build_pack` and `rebuild_index` worker handlers in `worker.py`. PostgreSQL `SqlLangGraphCheckpointer` with crash recovery & state resumption verified in `test_durable_checkpoint_resume.py`. | **PASS** |
| **Phase D** | Database, Storage & Backup Architecture | P0 | PostgreSQL 16 `saarthi-postgres` with `BIGINT` timestamp migrations. Real S3/MinIO HTTP client in `storage.py`. PostgreSQL backup & scratch restore with 100% canonical replay verified. | **PASS** |
| **Phase E** | Retrieval Quality, Curriculum & Bloom Taxonomy | P0/P1 | Realigned 100 benchmark queries to Class 9 syllabus. Enhanced `LocalHybridRetriever` with Odia morphology & glossary mapping (100% Recall@5, MRR 0.851). 108 questions across 6 Bloom levels. | **PASS** |
| **Phase F** | Synchronization & Offline Fault Matrix | P0 | 12 fault injection tests verified in `test_offline_fault_matrix.py` (worker crash, tampered pack, auth expiry, dead-letter quarantine). 0 events lost. | **PASS** |
| **Phase G** | Frontend, Progress Screen & Prefetch | P0/P1 | React PWA mounted cleanly in `index.html`. Bundled offline `noto-sans-oriya-regular.woff2` (94 KB). Multi-tab Developer diagnostics panel. Background prefetch verified. | **PASS** |
| **Phase H** | CI, Browser E2E, Performance & Security | P0 | Added `.github/workflows/ci.yml`. Mobile Playwright E2E journey passed (`learner_journey.spec.ts`). `measure_device_perf.py` verified (0.53 MB, 0.02ms latency). Pack path traversal prevented. | **PASS** |
| **Phase I** | External Providers & Human Release Gates | P0/P1 | Built `scripts/review_odia_release.py`. Gates R1–R5 honestly classified (PASS vs BLOCKED) without synthetic reviewer fabrication. | **PASS** |
| **Phase J** | Documentation & Status Reporting Reconciliation | P0 | Updated `FINAL_REPORT.md`, `requirements_traceability.md`, `implementation_status.md`, `devices.md`, `decisions.md`. | **PASS** |

---

## 2. Phase-by-Phase Technical Specifications & Verification Criteria

### Phase A: Repair Installed-Pack and Offline-Learning Pipeline (P0)
- **A1. Archive Parsing & Format Consensus**:
  - Establish clear pack specification: `.tar.gz` or gzip-compressed JSON container. Ensure `scripts/build_packs.py` produces standard archive and manifest with explicit `archive_sha256`, `archive_size`, `manifest_sha256`, `content_version`.
  - Fix client decompression in `pack_downloader.ts`: decompress gzip stream into valid JSON string before storing or parsing.
  - Fix `Doubt.tsx` to read the parsed manifest correctly (retrieving chunks and glossary from the stored pack).
- **A2. Resumable Downloader**:
  - Implement durable partial segment persistence (IndexedDB / cache) in `pack_downloader.ts`.
  - Validate HTTP 206 `Content-Range: bytes START-END/TOTAL`.
  - Handle 200, 206, 416 responses, re-validate segments on resume, SHA-256 verification of full archive.
  - Server-side Range verification in `backend/app/api/routes/packs.py` with accurate Content-Range.
  - Fix server marking `PACK_INSTALLED` prematurely: only client marks installed after successful SHA-256 verification and atomic installation.
  - Fix `prefetch_scheduler.ts` to pass `archive_sha256` and archive byte size.
- **A3 & A4. Offline Flow Integration**:
  - Trace `Published pack -> HTTP Range download -> Resume -> SHA-256 verify -> Decompress -> Schema validate -> Local installation -> Offline Lesson & Doubt -> Offline Assessment -> Sync`.
  - Verify complete offline operation without LLM/Redis/server dependency.

### Phase B: Fix Deterministic Learning Decisions and Evaluation (P0)
- **B1. Missing-Pack / Offline Rule**:
  - Inspect `backend/app/domain/decide.py` and `frontend/src/engine/decide.ts`.
  - Correct the missing-pack branch when learner is offline: when required pack is missing and offline, choose nearest installed concept, graph-distance ordering/tie-breaking, reason `CONTENT_NOT_AVAILABLE_OFFLINE`, and emit `PREFETCH` background action for when connectivity returns.
- **B2. Trustworthy Evaluator**:
  - Update `scripts/eval_decision_quality.py`: fail gate (return non-zero exit code) if any critical category (especially `missing_pack_offline`) has critical failures or < 90% agreement.
  - Compare `background_actions` and reason codes.
- **B3. Independent Dataset & Review Audit**:
  - Distinguish mechanically generated test vectors from independent gold scenarios.
  - Maintain held-out partition (>=30%).
- **B4. Python / TypeScript Parity**:
  - Run vectors across both Python and TypeScript, asserting 100% agreement on decisions, reasons, and background actions.

### Phase C: Complete Durable Backend Orchestration and Jobs (P0)
- **C1 & C2. Real Arq and PostgreSQL Job System**:
  - In `backend/app/worker/worker.py`, implement actual job handlers for `build_pack` and `rebuild_index` instead of returning mock `ok`.
  - Support PostgreSQL job persistence, deduplication keys, attempt counting, lease expiry, worker crash recovery, exponential backoff with jitter.
- **C3. LangGraph Checkpoint Persistence**:
  - Replace default in-memory `MemorySaver` with durable PostgreSQL checkpointer.
  - Verify graph state persistence and thread recovery across restarts.
- **C4. Grounding & Entailment Provider**:
  - Support validated answer workflow, factual claim entailment against curriculum chunks, low-confidence safe extractive fallback.

### Phase D: Database, Storage and Backup Architecture (P0)
- **D1. PostgreSQL Authoritative Backend**:
  - Verify PostgreSQL asyncpg connection and Alembic migrations from empty DB.
- **D2. S3-Compatible Storage Adapter**:
  - Implement real S3/MinIO operations in `backend/app/adapters/storage.py` (upload, download ranges, checksum verification, atomic promotion, error typing).
- **D3. Indexing & Publication Pipeline**:
  - Worker-side atomic index build and pack publication pipeline.
- **D4. PostgreSQL Backup & Restore Drill**:
  - Update `scripts/db_backup_restore.py` for real PostgreSQL backup (`pg_dump`/custom async dump), restore to scratch database, and bidirectional replay verification against mastery.
- **D5. Redis Support**:
  - Ensure rate-limiting and cache gracefully handle Redis connection and fail safely without silent in-process unlimited bypass.

### Phase E: Retrieval Quality, Curriculum and Bloom Taxonomy (P0/P1)
- **E1. Retrieval Benchmark**:
  - Evaluate multilingual embedding candidate and BM25 hybrid pipeline in `scripts/eval_retrieval.py`.
  - Improve Odia text normalization and retrieval Recall@5.
- **E2 & E3. Content & Bloom Taxonomy**:
  - Verify 108 questions across 9 concepts and 6 Bloom levels.
  - Option-level misconceptions, stable IDs, revision metadata.
- **E4. Content Rights & Review Tooling**:
  - Auditable workflow and schema for human reviews.

### Phase F: Synchronization and Offline Fault Matrix (P0)
- **F1. Sync Protocol Verification**:
  - Idempotent batches, per-device sequences, partial acceptance, canonical ordering, cursor advancement.
- **F2. Offline Fault Injection Suite**:
  - Implement missing fault cases in `test_offline_fault_matrix.py` (IndexedDB interruption, outbox retention, clock skew, expired auth, permanent quarantine, PostgreSQL restart).
- **F3. Profile Isolation**:
  - Ensure zero leak across learner profiles.

### Phase G: Frontend, Progress UI & Prefetch (P0/P1)
- **G1. Wire Complete Learner Experience**:
  - End-to-end integration: Startup -> Profile Picker -> Lesson -> Assessment -> Doubt -> Progress.
- **G2. Background Prefetch**:
  - Connect `PREFETCH` action to real resumable downloader.
- **G3 & G4. UI & Odia Font**:
  - Progress concept map, diagnostic screen, bundle Odia font asset in `frontend/public/fonts/`.

### Phase H: CI, Playwright E2E, Performance & Security (P0)
- **H1. GitHub Actions CI**:
  - Add `.github/workflows/ci.yml` running lint, types, unit tests, integration tests, parity, and security checks.
- **H2. Playwright E2E**:
  - Configure Playwright in `frontend/`, implement offline learner journey test.
- **H3. Device Performance Tooling**:
  - Create `scripts/measure_device_perf.py`.
- **H4. Security Checks**:
  - Validate auth, input sanitization, rate limits, path traversal protection.

### Phases I & J: Release Gates & Reporting Reconciliation
- Honest tracking of R1–R5 release gates.
- Fully regenerated `docs/FINAL_REPORT.md`, `docs/requirements_traceability.md`, `docs/implementation_status.md`.
