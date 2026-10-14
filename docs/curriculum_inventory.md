# SAARTHI Curriculum Inventory — Phase 6 (14 October 2026)

Source of truth: `curriculum/ch01|ch02|ch03/manifest.json` + `curriculum/glossary.json`,
built by `scripts/build_packs.py` into `packs/pack_class9_science_or_v1-1.0.0.json`.
All numbers below were computed from the **rebuilt** pack, not from prior docs.

## 1. Content counts (verified)

| Item | Count |
|---|---|
| Chapters | 3 (ch01 Matter in Our Surroundings, ch02 Motion–Measurement, ch03 Tissues) |
| Concepts | 9 (c0001–c0009) |
| Chunks | 18 |
| Questions | 39 (27 MCQ, 12 short_answer) |
| Glossary entries | 30 |
| Subjects | science only — **no Geography content exists anywhere in the repo** |

## 2. Answer-key defect found and corrected

`q_ch01_c0002_02` asked: *"An object with relative density 2.0 — what will it do in water?"*
The source manifest's answer key said it **floats** (option 1), and the explanation
repeated the error. Relative density 2.0 > 1 ⇒ the object **sinks** (option 0).

- Corrected `correct_option` to 0 and rewrote `explanation_or` in `curriculum/ch01/manifest.json`.
- The distractor "floats" is now explicitly mapped to the misconception tag
  `relative_density_float` (the learner's answer exhibits exactly that belief).
- The catalog label in `backend/app/domain/diagnose.py` was updated to match the
  misconception the distractor actually displays.
- **Teacher review is still required** to confirm the corrected wording and all
  other annotations below. Nothing here claims pedagogic validation.

## 3. Metadata coverage (annotation completeness ≠ teacher-review completeness)

| Metadata | Coverage | Notes |
|---|---|---|
| `bloom_level` | 39/39 | remember (unit/definition/fact recall), apply (numeric/formula), understand (short-answer explain/compare). No analyze/evaluate/create — no such items exist in the pack. |
| `misconception_tag` (question level) | 3/39 | pre-existing: relative_density_float, displacement_zero_in_circular, neuron_vs_matrix |
| `misconception_options` (distractor mapping) | 3/39 | added where the pack's own explanation supports the mapping: q_ch01_c0002_02 ("floats"→relative_density_float), q_ch01_c0002_01 (inverted ratio→density_ratio_inverted, new tag), q_ch02_c0004_01 (distance values→displacement_zero_in_circular) |
| `review_status: pending_teacher_review` | 39/39 | every annotated question. **teacher_reviewed: 0/39.** |

**Teacher-review completeness is zero.** All annotations are machine-authored
conservative mappings flagged for review; the two new catalog labels
(`density_ratio_inverted`, plus the reworded `relative_density_float`) are
candidate descriptions, not validated diagnoses. Items with **no** reliable
mapping (e.g. q_ch03_c0009_02, where the distractors are genuine neuron parts)
were deliberately left unmapped rather than guessed.

## 4. Schema validation added

`scripts/build_packs.py:validate_question` now rejects:
- invalid `bloom_level` values (must be one of the six Bloom levels),
- `misconception_options` keys that are not valid option indices, or that
  point at the **correct** option, or empty tags,
- invalid `review_status` values.

Backend `Question` schema additionally validates Bloom levels and passes
`review_status` through the pack loader. Legacy packs without these fields
still load unchanged (verified by the test suite).

## 5. Odia / structured-answer review

All 39 questions are Odia-first (`prompt_or`, options, `explanation_or`; 12
short-answer items carry Odia `rubric_or`). MCQ flow is index-based
(`correct_option`), so no English-only assumptions affect structured answers.
The relay/rooms layer (Phase 2) classifies Odia free text via bilingual
keyword sets. Remaining risk: the relay bank content itself is English demo
material with Odia keywords only (documented in Phase 2).

## 6. Geography scope gap

No Geography chapters, concepts, or questions exist. The Science pack does
**not** fulfill any Geography requirement. Proposed teacher-reviewable pilot:
one Geography chapter (e.g. Class 9 "India–Size and Location" or "Physical
Features of India", Odia-first, mirroring the ch01 structure: 3 concepts,
≥1 chunk each, ≥3 questions per concept with Bloom + misconception metadata,
all `pending_teacher_review`) once a teacher reviewer is available. Do not
generate this automatically.

## 7. Reproduce

```bash
backend/.venv/bin/python scripts/build_packs.py   # rebuild + validate
cd backend && .venv/bin/python -m pytest -q        # 366 passed
```
