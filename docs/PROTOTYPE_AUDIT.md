# SAARTHI Prototype Audit

Date: 2026-10-14
Status: Evidence-based audit of the repository as checked in this workspace.

## Executive summary

The repository is not a blank prototype. It contains a functioning backend, deterministic learning engine, pack pipeline, and study-room scaffolding. The most important verified baseline is:

- Backend tests: 299 passed in 2.88s (`backend/.venv/bin/python -m pytest -q`)
- Frontend build: succeeded (`cd frontend && npm install --silent && npm run build`)
- The pack builder had a real checksum/gzip integrity bug and was corrected and revalidated.

The repository is therefore in a working MVP state with a small but important integrity defect fixed, but not every large-scale phase in the prompt is fully complete. The required audit distinguishes confirmed implementation from partial or external-blocked work.

## Feature inventory

| Feature ID | Name | Status | Evidence | Notes |
|---|---|---|---|---|
| F-01 | Curriculum pack builder | IMPLEMENTED_AND_VERIFIED | `scripts/build_packs.py`, `packs/*.json`, backend test suite | Rebuilt and validated; checksum/gzip mismatch corrected |
| F-02 | Deterministic learning engine | IMPLEMENTED_AND_VERIFIED | `backend/app/domain/decide.py`, `frontend/src/engine/decide.ts`, `tests/fixtures/rule_vectors.json` | Shared ruleset and vector validation |
| F-03 | Assessment and mastery updates | IMPLEMENTED_AND_VERIFIED | `backend/app/services/assessment_service.py`, `backend/tests/test_assessment_service.py` | BKT and event persistence validated |
| F-04 | Event sync / idempotent replay | IMPLEMENTED_AND_VERIFIED | `backend/app/services/sync_service.py`, `backend/tests/test_sync.py` | Pending events and canonical replay confirmed |
| F-05 | Doubt orchestration and RAG | IMPLEMENTED_AND_VERIFIED | `backend/app/orchestration/graph.py`, `backend/tests/test_orchestration.py` | Provider fallback and validation are in place |
| F-06 | API surface and health | IMPLEMENTED_AND_VERIFIED | `backend/app/api/routes/*`, `backend/app/main.py` | HTTP endpoints and authorship patterns are present |
| F-07 | Frontend PWA and offline UX | IMPLEMENTED_AND_VERIFIED | `frontend/src/*`, `vite.config.ts` | Build passes and app shell is generated |
| F-08 | Study Rooms backend | PARTIALLY_IMPLEMENTED | `backend/app/services/rooms_service.py`, `backend/app/api/routes/rooms.py`, `backend/tests/test_rooms.py` | Room lifecycle scaffolding exists but the full prompt’s deeper audit phases are not fully verified here |
| F-09 | PostgreSQL 16 production config | PARTIALLY_IMPLEMENTED | `docker-compose.yml`, `backend/app/core/settings.py` | Config supports Postgres, but no live PostgreSQL integration run was executed in this environment |
| F-10 | Full event synchronization semantics per prompt | PARTIALLY_IMPLEMENTED | `SyncService` and schema definitions | It meets the repo’s current MVP contract, but the broader prompt’s stricter transactional semantics are not all proven here |
| F-11 | Resource-aware agent and room lifecycle | PARTIALLY_IMPLEMENTED | room + agent service files | Present but not fully exhaustively tested under the full phase plan |
| F-12 | External model integrations | BLOCKED_BY_EXTERNAL_DEPENDENCY | AI provider stubs | Requires HF/OpenAI credentials for live model execution |

## Confirmed implementation status by area

### Backend infrastructure

Status: IMPLEMENTED_AND_VERIFIED

Confirmed components:

- FastAPI app factory and lifecycle in `backend/app/main.py`
- Versioned API routes in `backend/app/api/routes/`
- Settings and validation in `backend/app/core/settings.py`
- Structured error handling in `backend/app/core/errors.py`
- Persistence adapter and schema loader in `backend/app/adapters/persistence/__init__.py`
- Repository layer in `backend/app/adapters/persistence/repositories.py`

### Deterministic learning flow

Status: IMPLEMENTED_AND_VERIFIED

Confirmed components:

- Shared ruleset in `packages/ruleset/rules.json`
- Domain logic in `backend/app/domain/decide.py` and `backend/app/domain/bkt.py`
- Assessment evaluation in `backend/app/domain/assess.py`
- Service orchestration in `backend/app/services/assessment_service.py`
- Regression coverage in `backend/tests/test_decide_vectors.py` and `backend/tests/test_assessment_service.py`

### Synchronization and event correctness

Status: IMPLEMENTED_AND_VERIFIED for core MVP behavior

Confirmed components:

- Idempotent event handling in `backend/app/services/sync_service.py`
- Dead-letter and canonical mastery replay in repository + service layer
- Tests in `backend/tests/test_sync.py`

Important caveat:

This satisfies the repository’s current implementation and test contract, but it does not yet prove every advanced transactional/ordering requirement from the prompt’s later phases, especially the stricter multi-transaction event + mastery + cursor semantics and concurrency conditions.

### Study Rooms backend

Status: PARTIALLY_IMPLEMENTED

Confirmed components:

- `backend/app/api/routes/rooms.py`
- `backend/app/services/rooms_service.py`
- `backend/app/domain/rooms.py`
- `backend/app/services/rooms_agent.py`
- `backend/app/services/rooms_content.py`
- `backend/app/services/rooms_seed.py`
- `backend/tests/test_rooms.py`

Evidence suggests room creation, membership, expiry logic, and seeded demo content are present. However, this implementation was not exhaustively audited against the expanded prompt’s full lifecycle, auth, and concurrency requirements in this pass, so it should be treated as partially implemented rather than fully verified.

### PostgreSQL support

Status: PARTIALLY_IMPLEMENTED

The project declares PostgreSQL support in `docker-compose.yml`, `backend/app/core/settings.py`, and the persistence layer. The current environment did not run a live PostgreSQL migration path or Postgres-backed integration tests, so the claim is limited to configuration support rather than verified Postgres behavior.

### External dependencies and blockers

Status: BLOCKED_BY_EXTERNAL_DEPENDENCY

The live AI/provider path requires external credentials or services (HF token, OpenAI-compatible endpoint, optional FAISS dependencies). The code includes typed provider wrappers, but the environment here is not configured for those live paths.

## Defects found and repaired during this audit

### Pack integrity bug

Issue:

- `scripts/build_packs.py` generated a checksum for a different blob than the final JSON artifact and wrote a gzip payload that did not match the canonical JSON bytes.

Fix:

- Canonicalize the manifest body before computing `checksum_sha256`.
- Keep JSON and gzip payloads aligned.
- Rebuild the pack and validate the generated output.

Verification:

- `backend/.venv/bin/python scripts/build_packs.py`
- `backend/.venv/bin/python -m pytest -q backend/tests/test_pack_build.py`
- Result: 9 passed in 0.02s

## Baseline verification evidence

Commands run:

1. `cd /home/elemento/SAARTHI && backend/.venv/bin/python -m pytest -q`
   - Result: 299 passed in 2.88s

2. `cd /home/elemento/SAARTHI/frontend && npm install --silent && npm run build`
   - Result: Vite production build succeeded; PWA assets generated.

3. `cd /home/elemento/SAARTHI && backend/.venv/bin/python scripts/build_packs.py && backend/.venv/bin/python -m pytest -q backend/tests/test_pack_build.py`
   - Result: 9 passed in 0.02s

## Final status summary

The project is operational and test-passing for the verified backend/frontend surface in this workspace. It is not fully verified against the expanded end-to-end prompt’s later phases for large-scale database/event-room semantics in a live PostgreSQL environment, and those items should be treated as partially implemented or blocked rather than fully complete.

## Deliverables expected by the master prompt

- Audit file: present (`docs/PROTOTYPE_AUDIT.md`)
- Phase log: present (`docs/PHASE_IMPLEMENTATION_LOG.md`)
- Development guide: present (`docs/DEVELOPMENT.md`)
- Migration and source changes: limited verified fixes applied to the pack builder and test pipeline
- Remaining wider prompt phases: not all fully completed in this workspace pass; the repo is left in a stable, verified state and the remaining items are documented as partial or blocked
