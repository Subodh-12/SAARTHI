# SAARTHI — Architectural & Implementation Decisions

This document reconciles the authoritative decisions from **SAARTHI — Design Document v2** (Section 18: Open Decisions D1–D10) with the engineering resolutions adopted during implementation.

---

## Part 1: Design Document v2 Section 18 Decisions (D1 – D10)

| # | Decision Topic | Status | Confirmed Resolution & Engineering Rationale | Owner |
|---|---|---|---|---|
| **D1** | Rights to use and redistribute Class 9 Science textbook text | **RESOLVED (Default)** | Original concept notes, worked examples, and definitions were authored directly from the NCERT/BSE Odisha Class 9 Science syllabus (`curriculum/ch01`, `ch02`, `ch03`). No unpermitted textbook scans or copyrighted third-party assets are published. `curriculum/review_metadata.json` tracks source licenses (CC-BY-4.0 / Original Team Authored). Gate R2 satisfied. | Odia & Evaluation Lead |
| **D2** | Three chapters forming the MVP slice | **RESOLVED** | The three fundamental Class 9 Chemistry/Matter chapters: **Chapter 1 (Matter in Our Surroundings - 3 concepts)**, **Chapter 2 (Is Matter Around Us Pure - 3 concepts)**, and **Chapter 3 (Atoms and Molecules - 3 concepts)**. Total 9 concepts covered comprehensively. | Team |
| **D3** | LLM, embedding model, ASR and TTS provider selection | **RESOLVED (Interface & Fallback)** | Typed provider adapters implemented (`app/adapters/ai/`). Server doubt loop uses `LocalHybridRetriever` (BM25 + Glossary + RRF) and `DeterministicOdiaEntailer` validator with graceful extractive fallback when remote LLM credentials (`HF_TOKEN` / `OPENAI_API_KEY`) are omitted. Offline mode uses 100% deterministic rule engine + extractive answer. | Agentic AI Lead & Odia Lead |
| **D4** | Mid-evaluation checkpoint format | **RESOLVED** | Evaluation scripts (`scripts/smoke_e2e.py`, `scripts/eval_decision_quality.py`, `scripts/eval_retrieval.py`, `scripts/db_backup_restore.py`) are fully automated and reproducible via CLI. | Team |
| **D5** | Children's data obligations before pilot (Gate R1) | **RESOLVED** | Pseudonymous UUID learner IDs only (`lrn_...`, `dev_...`). Schema strictly forbids real names, phone numbers, location data, contacts, or ad IDs. No live pilot with minors; seeded evaluation personas only. | Team with Faculty Advice |
| **D6** | Hosting provider and compute architecture | **RESOLVED** | Docker Compose specification supporting PostgreSQL 16, Redis 7, MinIO, and FastAPI backend service. Stateless compute boundary; durable stores retain all state. | Backend Lead |
| **D7** | On-device language model for offline doubts | **RESOLVED (Decided: NO)** | No heavy on-device LLM on the low-end 2GB phone. Offline doubts are resolved extractively from the installed pack (BM25 + glossary). Deterministic rules decide next learning actions in pure TypeScript (<50 KB). | Agentic AI Lead |
| **D8** | Reference phone, browser, and network profile | **RESOLVED** | Android 2GB RAM reference phone, Chrome stable, throttled network profile (400 kbps downlink, 400 ms RTT) documented in `docs/devices.md`. | Frontend Lead |
| **D9** | Multi-device learners | **RESOLVED (Decided: Out of Scope for MVP)** | Correctness is strictly scoped to one active device per learner in MVP. Enforced by unique constraint `UNIQUE (active_device_id)` in `learner_profiles`. Second device sync attempt is rejected with `LEARNER_NOT_LINKED`. Multiple learners may safely share one phone. | Team |
| **D10** | Voice in the MVP demo | **RESOLVED (Decided: Text-First P0)** | Voice input/output (ASR/TTS) is P1. Offline learning is 100% text and tap-based. Voice button is only rendered when online and enabled. | Odia Lead |

---

## Part 2: Implementation & Architectural Resolutions

### D-101 — Persistence Backend: Dual SQLite / PostgreSQL 16 Architecture
- **Decision:** SQLite via `aiosqlite` is the default local and test runner store for zero-dependency execution. PostgreSQL 16 is supported via async SQLAlchemy (`DATABASE_URL=postgresql+asyncpg://...`) and Alembic migrations (`alembic/versions/`).
- **Rationale:** Ensures 100% of integration tests execute locally in CI without requiring live Postgres daemon, while maintaining identical SQL contracts.

### D-102 — Arq Durable Worker and PostgreSQL Job Table
- **Decision:** Arq worker framework backed by a durable `jobs` table in PostgreSQL/SQLite (`job_id, type, payload_json, dedupe_key, status, attempts, max_attempts, next_run_at, lease_expires_at, last_error`).
- **Recovery:** A reconciler task runs every 60 seconds and re-enqueues running jobs with expired leases. Non-retryable errors (gate failures) transition immediately to `dead`; retryable errors follow exponential backoff (5s base, factor 2, ±20% jitter, cap 10m, max 6 attempts). Admin route `GET /api/v1/admin/jobs` provides operator visibility.

### D-103 — LangGraph Orchestration State Machine
- **Decision:** Doubt branch implemented as a compiled LangGraph `StateGraph` (`translate -> retrieve -> generate -> validate -> END`) with checkpointer support.
- **Autonomy Boundaries:** Tool calls capped at 3; 12-second execution budget; 1 retry per tool before extractive fallback. LLM never chooses the learning action.

### D-104 — Integer Basis-Point Mastery Representation
- **Decision:** Learner mastery is stored and computed strictly as integer basis points ($0$ to $10,000$ bp), using integer arithmetic with half-up rounding.
- **Rationale:** Prevents cross-language floating-point divergence between Python server and TypeScript client.

### D-105 — Profile Isolation on Shared Devices
- **Decision:** Frontend uses separate profile-scoped IndexedDB databases (`saarthi-profile-{learnerId}`) and one shared database (`saarthi-shared`). All profile operations route exclusively through `ProfileSession`. Switching profiles clears in-memory state and closes the database.
