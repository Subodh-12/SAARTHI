# SAARTHI Jury Evidence

## 1. Executive summary
SAARTHI is a learner-facing, offline-first study assistant designed for Odia-medium class 9 science learners. The repository contains a working prototype that combines a deterministic decision engine, local persistence, offline-safe sync patterns, room workflows, and an Odia-first interface. The implementation is strongest where it is grounded in repository-owned logic and tests; external live services, physical device validation, and native human Odia review remain explicitly blocked unless a proper environment and review process are supplied.

The current evidence supports the claim that the local implementation works as a verified prototype in this workspace. It does not support claims of production readiness, classroom efficacy, or live cloud AI competence without separate validation.

## 2. Existing foundation
The repository was not treated as a blank slate. The working foundation already included:

- a FastAPI backend and domain logic in [backend/app](../backend/app)
- a Vite React frontend in [frontend/src](../frontend/src)
- curriculum and pack metadata in [curriculum](../curriculum) and [packs](../packs)
- a ruleset in [packages/ruleset/rules.json](../packages/ruleset/rules.json)
- tests in [backend/tests](../backend/tests) and [frontend/tests](../frontend/tests)
- audit and implementation reports in [docs/PROTOTYPE_AUDIT.md](PROTOTYPE_AUDIT.md), [docs/FINAL_REPORT.md](FINAL_REPORT.md), and [docs/requirements_traceability.md](requirements_traceability.md)

The Phase 7 and Phase 8 work reused the existing implementation and only repaired verified defects or completed missing evidence, rather than rewriting the system.

## 3. Architecture
- Frontend: React + TypeScript + Vite + PWA shell; local state mapped to IndexedDB-style persistence and room screens.
- Backend: FastAPI + Python services and domain modules for decision-making, assessment, room lifecycle, and sync.
- Persistence: local learner state, cached packs, and pending events; room + learner state are kept in the same repository model and validated by the existing test suite.
- Curriculum engine: deterministic question selection, misconception tags, Bloom metadata, and next-action logic.
- Synchronization: event queue + replay patterns are used to preserve learner state when connectivity is interrupted.
- Localization: the canonical Odia dictionary lives in [frontend/src/i18n/or.ts](../frontend/src/i18n/or.ts), and room UI labels were aligned to it.

## 4. Diagnostic learning loop
The implemented learning loop in the repository follows the actual product flow:

1. present a question or lesson item,
2. record the learner response,
3. evaluate correctness and candidate misconception,
4. select a follow-up or relevant concept,
5. verify evidence or a discriminating check,
6. update mastery state,
7. recommend the next learning action.

This behavior is grounded in the domain layer rather than a simulated UI-only implementation. The main source areas are [backend/app/domain/assess.py](../backend/app/domain/assess.py), [backend/app/domain/bkt.py](../backend/app/domain/bkt.py), [backend/app/domain/decide.py](../backend/app/domain/decide.py), and the app services that connect them to the API and frontend.

## 5. BKT integration
The repository contains an explicit mastery model and event-driven state logic. The BKT-style semantics are not treated as a generic placeholder; the system uses learner response data, evidence states, and deterministic next decisions to update mastery and drive the next action. The implementation remains consistent with the repository’s documented semantics and the verified decision vectors.

The key evidence is in the domain and test files, especially [backend/app/domain/bkt.py](../backend/app/domain/bkt.py), [backend/app/domain/decide.py](../backend/app/domain/decide.py), and the matching tests under [backend/tests](../backend/tests).

## 6. Bloom's Taxonomy
The curriculum dataset includes Bloom metadata and the app uses it as part of the question-selection and learning-selection strategy. The repository’s evaluation suite and curriculum materials distinguish question difficulty and cognitive level, and the decision logic is designed to respect those distinctions rather than treat all questions as equivalent.

The relevant evidence is in the pack data under [packs/pack_class9_science_or_v1-1.0.0.json](../packs/pack_class9_science_or_v1-1.0.0.json), the decision logic, and the curriculum validation/reporting files in [docs](../docs).

## 7. Regional-language behavior
The Odia-first UX is a real implemented requirement in the app, not just a decorative claim. The canonical translation layer is [frontend/src/i18n/or.ts](../frontend/src/i18n/or.ts), and the remaining room screens were repaired so they consume the shared Odia keys instead of hardcoded English labels.

The project also includes design and release-gate language around native-review quality. The official rubric is explicit in [scratch/design_doc_v2.txt](../scratch/design_doc_v2.txt) and [docs/native_odia_review_report.md](native_odia_review_report.md): correctness, fluency, register, and terminology. However, the design document explicitly marks the human review gate as blocked until a native Odia reviewer signs off.

## 8. Offline-first behavior
The app is designed to operate without a live backend during key learning flows. The verified local evidence supports the claim that:

- the frontend build still succeeds,
- the app shell persists and loads properly,
- learner events and local state are stored in a durable local mechanism,
- the decision engine and relevant content logic remain available offline,
- retry and replay patterns are used when synchronization is interrupted.

This is a local prototype claim, not a claim that every live network/AI/cloud feature is production-validated.

## 9. Rooms and collaboration
Rooms are implemented at the app layer and API/service layer. Verified room behaviors for this workspace include:

- create room,
- join room,
- list rooms,
- send and retrieve messages,
- render room details and activity views,
- preserve room form drafts,
- keep the room UI in Odia.

The core UI files are [frontend/src/screens/rooms/Rooms.tsx](../frontend/src/screens/rooms/Rooms.tsx) and [frontend/src/screens/rooms/RoomView.tsx](../frontend/src/screens/rooms/RoomView.tsx), with supporting service code under [backend/app/services](../backend/app/services).

## 10. Evaluation results
The repo has actual verification output, and the results below are taken from the local environment.

1. Backend regression suite
   - Command: `cd /home/elemento/SAARTHI && .venv/bin/python -m pytest -q`
   - Result: 343 passed in 9.24s

2. Room localization regression + frontend build
   - Command: `cd /home/elemento/SAARTHI/frontend && npx vitest run tests/rooms_i18n.test.ts && npm run build`
   - Result: 1 test file passed; production Vite build succeeded

3. Official release-gate status
   - Design Document v2 explicitly sets the Odia quality gate as a native-review requirement.
   - The repo records this as blocked in [docs/requirements_traceability.md](requirements_traceability.md) and [docs/native_odia_review_report.md](native_odia_review_report.md).

4. Additional evidence file
   - [docs/PROTOTYPE_AUDIT.md](PROTOTYPE_AUDIT.md)
   - [docs/requirements_traceability.md](requirements_traceability.md)
   - [docs/FINAL_REPORT.md](FINAL_REPORT.md)

## 11. Research and prior art
The repository contains an in-project design specification and traceability matrix, and the official design doc is the strongest available source for the project’s intended rubric and release criteria. The current repo does not claim a full external literature review beyond those in-project references, and any broader prior art should be treated as a separate research task if needed.

Verified source-level references in this repo:

- [scratch/design_doc_v2.txt](../scratch/design_doc_v2.txt): official project design document
- [docs/requirements_traceability.md](requirements_traceability.md): release-gate mapping and evidence status
- [docs/native_odia_review_report.md](native_odia_review_report.md): actual Odia review rubric and blocked gate status

The project’s defensible differentiation is not “novel by invention alone,” but rather a project-specific integration of deterministic learning decisions, local offline continuity, multilingual education support, and explainable next actions in a constrained classroom context.

## 12. Demonstration script
1. Start the app locally from the repository root using the repo’s normal startup instructions.
2. Open the app and confirm the Odia-first interface renders correctly.
3. Create or join a room and verify the room list and detail screens render in Odia.
4. Enter a room name or code, confirm persistence of the draft form value across UI re-renders.
5. Submit a message and confirm it appears in the room thread.
6. Open the room activity area and confirm actions appear in the expected room flow.
7. Run the backend pytest suite and frontend build checks.
8. Confirm that the release gate for native Odia human review remains explicitly blocked and not falsely claimed as passed.

## 13. Known limitations
The following limitations are part of the repo’s actual state and are not hidden by the evidence:

- native Odia human review remains blocked pending independent human sign-off,
- external production services and cloud AI integrations are not live-validated in this environment,
- classroom effectiveness and real-world learning gains are not proven here,
- broader multi-device or live deployment verification is still pending,
- the project remains local-environment validated rather than fully production-validated.

## 14. Claims the team can safely make
The repo supports the following evidence-backed claims:

- SAARTHI has a working local prototype and validated backend/frontend test coverage in this environment.
- The room UI and room draft workflow work as implemented.
- The app uses a canonical Odia language layer for the room experience.
- The backend regression suite passes.
- The frontend production build succeeds.
- The project maintains explicit release-gate honesty: blocked criteria are recorded as blocked instead of falsely marked as complete.

## 15. Claims that must not be made yet
The team should not claim any of the following without separate evidence:

- production deployment success,
- live multi-user room operation at real scale,
- real-world learning improvement results,
- native human approval of Odia quality,
- external AI provider reliability,
- official rubric compliance beyond the checked local environment,
- any classroom or institutional approvals.

The official rubric in [scratch/design_doc_v2.txt](../scratch/design_doc_v2.txt) requires native review for the Odia quality gate. That gate remains blocked and must be reported as such.

## Final status
The project is in a verified working state for the audited local environment, with the explicit room-language defect fixed and the evidence documented. The Native Odia review gate remains blocked pending independent human validation, which is consistent with the project’s own rubric and release-gate expectations.
