# SAARTHI Design Document v2 — Repository Compliance Audit

**Audit date:** 15 October 2026  
**Repository inspected:** `saarthi_main(7).zip` (291 files in the extracted tree, including generated/runtime artifacts)  
**Specification:** *SAARTHI — Design Document v2*, 57 pages  
**Scope:** Source inspection, targeted script execution, evaluation output, test layout, infrastructure/configuration, and comparison against design Sections 1–18 and Appendices A–B.

## Executive estimate

- **Implementation coverage:** approximately **65%**. About **35% of implementation work remains, or exists only as partial/inaccurate scaffolding**. This is an estimate of weighted requirements, not a literal count of PDF pages or files.
- **Acceptance/release verification:** approximately **35–40% adequately evidenced**. The project has useful tests and some evaluation scripts, but critical claims in the completion reports are unsupported, and multiple critical runtime paths are defective.
- **Current release posture:** **partially compliant offline-first MVP; not yet demonstrated to pass all P0 release gates**.

The codebase has advanced materially: active-profile recovery, PIN setup, profile picker, Bloom taxonomy, a 108-question curriculum, LangGraph nodes, Alembic files, a durable jobs table, pack range-download scaffolding, and prefetch scheduling now exist. The biggest remaining risk is integration correctness and evidence, not a lack of folders or classes.

## Direct checks performed

| Check | Observed result | Interpretation |
|---|---|---|
| `python scripts/build_packs.py --strict` | Exit 0; 3 chapters, 9 concepts, 18 chunks, 108 questions | The count/strict pack build succeeds for the current source manifests. It does not prove human review or rights approval. |
| `python scripts/eval_decision_quality.py` | 100% structural validity; 90.48% held-out agreement; prints `PASS` | The aggregate passes its own threshold, but one critical category has 0% agreement and the gate does not fail on that category. |
| Decision quality category `missing_pack_offline` | 0/10 matches | Critical behavior is wrong: missing-pack offline scenarios select `REMEDIATE` instead of the expected `CONTENT_NOT_AVAILABLE_OFFLINE` behavior and omit expected prefetch. |
| `PYTHONPATH=backend python scripts/eval_retrieval.py` | Recall@5 = 27%; MRR around 0.116; comparison model blocked | Materially below the report's 80% Recall@5 target; semantic retrieval is not validated to the expected level. The local environment also logged missing `rank_bm25`. |
| `PYTHONPATH=backend python -m pytest -q --disable-warnings --maxfail=25` | Collection failed with 11 errors because `langgraph` is unavailable in the current runtime | Full test suite not independently verified in this environment. `langgraph` is declared in requirements, so this result alone is not evidence of an intrinsic source bug. |
| Archive inspection | `.srt.tar.gz` is gzip-compressed JSON bytes, not a tar archive | Artifact extension/content and the design's multi-file pack description disagree; client must explicitly decode/decompress and validate the actual payload. |
| Repository infrastructure | No `.github/workflows`, no `scripts/measure_device_perf.py`, no Playwright dependency/config, no bundled `.woff`/`.ttf`/`.otf` font | CI, browser E2E, the cited performance command and required Odia font are absent from this archive. |

## Critical defects / gaps to fix first

### P0 — Offline pack install and doubt answering do not form a working end-to-end flow

**Files:** `frontend/src/lib/pack_downloader.ts`, `frontend/src/screens/Doubt.tsx`, `scripts/build_packs.py`, `backend/app/api/routes/packs.py`, `frontend/src/lib/prefetch_scheduler.ts`.

- The downloader appends binary archive bytes, then runs `new TextDecoder().decode(fullBuffer)` and saves that result as `manifest_json`. The downloaded file is gzip-compressed JSON, so this does not produce valid JSON.
- Offline doubt handling calls `JSON.parse(pack.manifest_json)` and expects `chunks` and `glossary`. After downloading the published archive, this path is expected to fail instead of answering from the installed pack.
- Partial segments live in a JavaScript `Map`, not durable storage. They are lost after a page reload or process restart.
- The client accepts HTTP 200 even when it requested a byte range. It does not verify the exact `Content-Range`; a server that ignores Range can cause the full file to be appended as if it were one segment.
- The server marks a pack as installed when the last archive byte is served, before client checksum validation and atomic installation have succeeded.
- The prefetch scheduler passes `candidate.byte_size` and `candidate.checksum_sha256` from a manifest rather than the archive-specific size/hash. That disagrees with the manual pack-install path and is likely to make auto-prefetch fail validation.
- The produced filename ends in `.srt.tar.gz`, but the builder writes gzip-wrapped JSON, not a tar archive containing the files listed in the design. Choose one explicit pack format and make producer, manifest and client agree.

**Required outcome:** persist resumable verified segments, validate `Content-Range` and archive hash/length, decode/decompress the selected format, validate pack schema, build the offline index, atomically install it, and only then record installation. Prove offline doubt + assessment still work after reload and after a failed upgrade.

### P0 — The decision-quality gate gives a false sense of success

**Files:** `scripts/gen_gold_scenarios.py`, `tests/fixtures/gold_decision_scenarios.json`, `scripts/eval_decision_quality.py`, `docs/decision_quality_report.json`, `backend/app/domain/decide.py` (or current decision module).

- The scenario generator writes reviewer names, review dates and `disagreement_resolved: true` into generated records. The repository does not independently substantiate these as real human labels or preserve a review/audit trail. Therefore the current data cannot be accepted as an independently labelled gold set merely from those fields.
- The evaluator reports 90.48% held-out agreement and exits successfully despite **0% agreement on missing-pack/offline cases**.
- Agreement comparison omits `background_actions` and ruleset version, although the design's parity and decision-quality contract includes them.
- The documented scenario coverage also includes low storage and weak network. Check whether the actual generator produces meaningful independent cases for every required category and whether reviewers labelled them before the rules were tuned.

**Required outcome:** obtain actual independent labels from the named subject expert and Odia lead, record disagreements, compare all decision fields, report each category, and fail the gate for catastrophic category failures rather than only checking one aggregate percentage. Correct the missing-pack branch and add regression tests.

### P0 — Backend durable execution/storage differs from the specified architecture

**Files:** `backend/app/worker/worker.py`, `backend/app/orchestration/graph.py`, `backend/app/adapters/storage.py`, `backend/requirements.txt`, `docker-compose.yml`, `scripts/dev.py`, `run.sh`.

- `execute_job_payload("build_pack", ...)` and `rebuild_index` return an `ok` result without actually building a pack or rebuilding an index. The source comments explicitly describe the real operation as future work.
- The app scripts and Compose setup do not start the worker. `WorkerSettings.redis_settings = None`; `arq` and `redis` are not listed in the backend requirements. The current implementation is a custom database-polling worker, not a deployed Arq worker satisfying the chosen stack.
- `S3MinIOStorage` delegates all operations to a local filesystem cache. It does not make authenticated S3/MinIO requests, despite its name and the completion report's claim.
- LangGraph is present, but the default graph uses `MemorySaver`; checkpoints are therefore process-memory state rather than durable PostgreSQL checkpoints.
- The design makes PostgreSQL 16 the system of record, with Arq backed by a PostgreSQL jobs table. Compose labels PostgreSQL/MinIO/Redis optional and uses SQLite by default. That is an explicit architecture deviation, not compliance with the decided stack.
- Alembic files exist, but the default persistence initialization still contains schema creation and ad-hoc migrations. The current tests target SQLite; this audit found no verified PostgreSQL empty-database + previous-release migration result. `asyncpg` is not in `backend/requirements.txt`.
- Redis middleware imports `redis.asyncio` dynamically, but the required Redis dependency is not listed. Production rate-limits/cache cannot be assumed to work from the base requirements.

**Required outcome:** either implement the documented production path and run it against PostgreSQL, Redis, MinIO/S3 and the durable worker, or revise the design document through an explicit owner-approved decision. Do not mark it complete based on schemas and adapters alone.

### P0 — Backup/restore is SQLite-only and overclaimed

**File:** `scripts/db_backup_restore.py`.

- The script uses SQLite `iterdump`, `sqlite3` restore and a SQLite async engine. It does not implement the design's nightly PostgreSQL logical backup flow.
- If the requested input DB does not exist, it creates a synthetic sample database and then runs a replay drill. This is useful as a smoke demonstration but is not evidence that a real production backup was restored.
- Replay verification compares each replayed key against the restored projection but does not detect extra restored mastery rows that are absent from replay.
- The design requires the backup to be restored and verified against restored accepted events before the checkpoint/demo. That PostgreSQL operational drill remains unverified.

### P0 — Fault matrix is incomplete relative to the spec

**File:** `backend/tests/integration/test_offline_fault_matrix.py`.

The file does contain useful tests for duplicates, partial acceptance, network interruption, clock skew, profile isolation, revision handling and a 200-event replay exercise. However:

- The 200-event test sends ordered batches and occasionally resends earlier events; it does not implement the documented random out-of-order delivery or actual injected request/app-kill failures in its body.
- The file lacks distinct executable tests for important cases such as application termination during a local transaction, storage full, expired access and refresh tokens after long offline use, unknown ruleset fallback, repeated sync failure, and visible quarantine after a true permanent rejection.
- The “permanent rejection” header does not match a dedicated permanent-rejection test; the partial acceptance test uses an unknown revision that is accepted with no mastery effect.
- The file has 9 test functions, not a demonstrated 16-case full release matrix. Several cases may be combined, but the full design matrix is not demonstrated by the current test set.
- Tests were not run in this audit environment because dependency collection failed.

**Required outcome:** map each Section 15 fault case to an explicit passing test or a documented manual protocol, run against the release build, and compare canonical replay for each case.

## Section-by-section status

Status meanings: **Mostly implemented** = source exists but important validation remains; **Partial** = material required behavior is missing or incomplete; **Not verified** = required proof/test/real environment evidence is absent.

| Design area | Current status | Remaining work |
|---|---|---|
| Sections 1–3: purpose, scope, requirements | Mostly implemented | Complete P0 end-to-end flows and acceptance evidence. P1 voice remains deferred as the document allows; P2 image input remains out of scope. |
| Section 4: deterministic agentic approach | Partial | The decision engine and graph exist, but independent decision labels are unverified and one major offline missing-pack category fails. |
| Section 5: system architecture | Partial | Implement real Arq execution, real S3/MinIO, durable PostgreSQL checkpoints, PostgreSQL production path and durable Redis integration. |
| Section 6: agent/decision rules | Partial | Fix missing-pack behavior; verify every terminal/guard rule and every output field; shared parity claimed but not independently rerun here. |
| Section 7: data model | Partial | Alembic files exist; prove fresh and previous-version PostgreSQL migrations and align runtime migrations with Alembic. Verify database types/constraints across PostgreSQL. |
| Section 8: API, sync outcomes, authentication | Partial | Many contracts and auth tests exist; prove the long-offline refresh lifecycle, permanent rejection/quarantine behavior and outbox retention through every fault case. |
| Section 9: offline client, ordering and replay | Partial / P0 blocker | Downloaded pack isn't converted to usable JSON, resume state isn't durable, and full offline acceptance matrix is not demonstrated. |
| Section 10: connectivity-aware planning | Partial | Prefetch uses wrong archive size/hash fields and does not demonstrably implement every storage/battery/connectivity rule. Validate reconnect remains non-blocking. |
| Section 11: content and RAG | Partial | 108-question size and chunk lengths pass builder; Recall@5 27% is below the stated 80% target, dense model comparison is blocked, source references are section labels rather than clear textbook page citations, and strict gate does not establish actual human review. |
| Section 12: Odia and voice | Partial | Online provider comparisons and independent native Odia review remain blocked/pending. Online ASR/TTS are P1; they should not delay P0 text-first offline behavior. No Odia font file is bundled in `frontend/public`. |
| Section 13: validation, safety and failures | Partial | Typed contracts and validators exist; verify complete ordered validation with real providers and failure injection. Prompt-injection and false-grounding paths need real integration evidence. |
| Section 14: tech stack, security and release gates | Partial | Stack differs from the decided PostgreSQL/Redis/S3/Arq architecture; CI, Playwright, security suite and operational deployment evidence are missing. R1, R3 and R5 explicitly remain pending; R2 is not independently evidenced. |
| Section 15: testing and release gates | Not passed | Independent 120-scenario gold set not substantiated; missing-pack category fails; full fault matrix unproven; physical-device latency/memory tests not run; retrieval target missed; Odia gate pending. |
| Section 16: roadmap/definition of done | Partial | Implementation status documents need to be reconciled with executed evidence and acceptance gates. |
| Section 17: demo and judging checklist | Partial | A demo can illustrate a development flow, but claims about the full offline, grounded retrieval and release guarantees should not be made until the blockers are fixed. |
| Section 18: risks/open decisions | Partial | Close owner decisions explicitly, including model selection, rights, child-data policy, reference device, and architecture deviations. |
| Appendix A: ruleset/reason codes | Mostly implemented, acceptance partial | Ruleset and parity files exist; fix missing-pack rule and validate all decision fields/categories, not only structural validity. |
| Appendix B: screens | Mostly implemented | Profile picker, progress and diagnostic screens exist; verify all flows work against the real stored pack and full offline mode. |

## Functional and non-functional requirements

| Requirement | Status | Reason |
|---|---|---|
| F1 profiles/PIN | Mostly implemented | New profile, PIN and startup recovery code exists; end-to-end switching/reload tests must run and prove strict isolation. |
| F2 grounded Odia doubt | Partial | Entailment code and providers exist; default is mock/deterministic rather than benchmark-selected real providers; offline installed-archive path is defective. |
| F3 assessments/mastery | Partial | 108-item content pack and BKT code exist; verify short-answer handling, grading, replay and taxonomy in a working end-to-end flow. |
| F4 deterministic next action | Partial / FAIL quality category | Core engine exists, but offline missing-pack behavior is 0/10 in the generated held-out set. |
| F5 offline learning | Partial / P0 blocker | Installed archive is saved as decoded binary text; offline doubt expects JSON with chunks/glossary. |
| F6 sync/retry | Partial | Core sync tests exist; complete specified fault matrix and actual dependencies not verified. |
| F7 profile isolation | Mostly implemented | Per-profile state stores and profile picker exist; run reload/switch/offline/browser tests. |
| F8 online ASR/TTS | Deferred P1 | Permitted to defer until P0 passes; no actual voice gate or integrations verified. |
| F9 prefetch | Partial | Scheduler exists but uses non-archive manifest fields and is not proven through actual installation. |
| F10 trace viewer | Mostly implemented | Trace endpoint and developer UI exist; end-to-end trace fields still need acceptance. |
| F11 expired-auth recovery | Partial/unverified | Some auth tests are claimed in docs; this environment did not run suite and fault matrix lacks this case. |
| F12 image input | Deferred P2 | Explicitly out of MVP critical path. |
| N1 launch time | Not verified | No physical device or measurement script. |
| N2 app + pack size | Partly measured | Builder sizes are small, but need installed-device measurement under documented protocol. |
| N3 local latency | Not adequately evidenced | Report attributes measurements to decision-quality evaluator, which does not time decisions; cited `scripts/measure_device_perf.py` is absent. |
| N4 online doubt latency | Not verified against actual selected provider | Local/mock/extractive latency is not equivalent to measurement with selected provider and end-to-end network conditions. |
| N5 no event loss | Not passed/evidenced | Current tests cover only part of the matrix and no test run was completed in this audit environment. |
| N6 2 GB / 20-minute stability | Not verified | Physical device evidence is pending; no cited measurement script exists. |
| N7 reproducibility | Mostly implemented | Rules and replay functions exist; rerun complete replay/property tests after fixes. |
| N8 minimal personal data | Mostly implemented | Pseudonymous learner schema exists; audit logging, deletion and policy obligations still need review. |
| N9 Python/TypeScript parity | Not independently verified here | Docs disagree on vector counts (162 vs 165) and tests could not complete collection in this environment. |

## Content-specific findings

**What passes:** the strict builder produced 108 questions for 9 concepts, 12 per concept and 4 per difficulty, plus 18 chunks within the builder's word-count range. The curriculum includes all six Bloom levels. MCQ incorrect-option tags are present in the checked MCQ data; one question with an empty option list is marked `short_answer`, so it should be validated with the short-answer schema rather than counted as a missing MCQ.

**What still needs work:**

- The strict builder validates counts and structural fields, but does not prove an independent human-reviewed record for each question or a real source-rights approval.
- The source references are labels like `ch01 §1.2`; the design calls for textbook page references. Decide whether section IDs meet the intended citation contract; otherwise add page-level references.
- `curriculum/review_metadata.json` asserts original authorship/CC-BY-4.0. This self-authored metadata is not the same as independent written permission or reviewer evidence.
- `scripts/eval_retrieval.py` reports 27% Recall@5 against its documented 80% target. Evaluate a second real multilingual dense model and improve retrieval before claiming RAG quality.
- The current question bank is small in total breadth (9 concepts across three chapters) by design. It meets the stated 3-chapter MVP shape, but expansion to all textbook chapters is explicitly later work, not a current P0 gap.

## Operational and repository tooling gaps

- `docs/devices.md` cites `scripts/measure_device_perf.py`, but the script is absent.
- No `.github/workflows` exists, so the specified pull-request CI is not configured in this archive.
- `frontend/package.json` has unit-test/build/lint/typecheck scripts but no Playwright dependency or browser E2E script.
- `frontend/public` contains icons but no bundled Odia font asset.
- The repository uses generated/static curriculum JS as well as pack JSON. Keep the source-of-truth flow and generated artifact process reproducible.
- The completion reports contradict each other: some claim N3 and R4 PASS; device and status notes still say hardware review is pending; parity counts vary (162 vs 165); the retrieval report documents 25–27% Recall@5 while the target is 80%. Status should be regenerated from test outputs, not manually asserted.

## Release gates R1–R5

| Gate | Status now | Why |
|---|---|---|
| R1 Children's data | **BLOCKED / PARTIAL** | Consent, retention, deletion, access and incident obligations need responsible review before real-student pilot. Seeded data only until then. |
| R2 Content rights | **NOT INDEPENDENTLY VERIFIED** | Repository metadata claims original/CC-BY content, but no independently auditable written approval/evidence is present in the archive. Do not publish restricted content without confirmation. |
| R3 Odia quality | **BLOCKED** | Independent native Odia reviewer score on the 100-question release set is pending. |
| R4 Offline integrity | **FAIL / NOT PROVEN** | Installed-pack offline path has a code defect; gold set has a zero-agreement offline category; fault test implementation does not prove every required condition, and suite did not run here. |
| R5 Target device | **BLOCKED** | Physical 2 GB Android measurements for launch, latency, memory and full learner loop have not been recorded; cited benchmark script is missing. |

## Prioritized implementation order

1. **Fix pack format/install/offline doubts first.** Align the built archive format, downloader, durable resume, checksum validation, parsed manifest/index and install acknowledgment. Fix prefetch metadata arguments and add browser tests for interrupted/complete/corrupt downloads.
2. **Fix the deterministic missing-pack branch.** Add direct unit tests for every terminal and edge rule; do not accept the evaluation as PASS while a release-critical category has 0% agreement.
3. **Make the test evidence real.** Create/review the actual independent gold set, compare all decision fields, make per-category regression a gate, and implement missing offline fault cases.
4. **Complete the real backend stack.** Implement true Arq worker startup and real `build_pack`/`rebuild_index` jobs, durable SQL checkpointer, real S3/MinIO adapter, production PostgreSQL driver/migrations and Redis dependencies. If intentionally not building that stack, change the design only with an explicit owner-approved decision.
5. **Fix backup/restore.** Implement PostgreSQL backup, scheduled operation and restore-to-scratch replay checking that compares the complete key sets both ways.
6. **Improve retrieval.** Resolve the current 27% Recall@5, compare at least two candidates on the same 100-query labelled set, document errors, and only then select the model.
7. **Add CI and real E2E/performance tooling.** GitHub Actions, Playwright offline-toggle learner journey, security/dependency audit and the actual device-measurement script.
8. **Close external release gates.** Obtain real human Odia review, responsible child-data approvals, source-rights confirmation and 2 GB Android measurements. These cannot be completed by code generation alone.
9. **Reconcile all status reports.** Regenerate requirement traceability and `FINAL_REPORT.md` from executed evidence; remove unsupported PASS claims.

## Final judgement

SAARTHI is no longer just a skeleton. The core decision engine, profile system, Bloom taxonomy and content pipeline have substantive code, and the current question count meets the 108-question target. But the repository is **not yet ready to claim full Design Document v2 compliance**.

The highest-risk remaining implementation defect is the installed-pack/offline-doubt path. The highest-risk evaluation defect is the misleading decision-quality PASS despite zero agreement in the missing-pack/offline category. The largest architecture gap is that the declared production services—PostgreSQL checkpoints, Arq jobs, actual S3/MinIO and Redis dependencies—are not fully connected to a running deployment path. The largest release blockers are native Odia review, children's-data policy approval, source-rights evidence and physical-device measurement.

Do not mark the project production-ready, or say all P0 gates pass, until these are fixed and their exact acceptance tests have executed successfully.
