# Changelog

## 2026-08-16

### Removed

- 24 prose-verdict test fixtures under `scripts/auditing/test-fixtures/` and their 25 pinning test methods across `scripts/tests/test_review_log.py` and `scripts/tests/test_synthesis_artifacts.py` (file removed): `malformed-no-status-no-questions.txt`, `questions-bare.txt`, `questions-bold.txt`, `questions-colon.txt`, `questions-heading.txt`, `questions-real.txt`, `questions-with-differentiation-and-removal.txt`, `removal-compliant-baseline.txt`, `removal-duplicate-none.txt`, `removal-row2-heading-lowercase.txt`, `removal-row3-heading-upper-colon.txt`, `removal-row4-bold-colon.txt`, `removal-row4-bold-no-colon.txt`, `removal-row5-titlecase-colon.txt`, `removal-row6-bulleted.txt`, `removal-row6-indented.txt`, `removal-row7-underscore.txt`, `removal-row8-no-colon.txt`, `removal-row9-omitted.txt`, `synthesis-changed.txt`, `synthesis-malformed-truncated.txt`, `synthesis-no-change.txt`, `synthesis-questions-quoted-reviewer.txt`, `synthesis-questions.txt`.

## 2026-08-11

### Added

- `scripts/auditing/references/authoring-guidance.md`: pruning taxonomy, differentiation examples, behavioral gates, rejected patterns.
- `scripts/auditing/OPEN_ITEMS.md`: settled calls, parity register, deferred lints, trial-gated removal candidates.
- 5 audit checks: `repo_root_skill_path` (issue), `heading_variant`, `heading_qualifier`, `heading_restated`, `activation_cues_in_skill_md` (warnings).
- `run_parallel_skill_reviews.sh`: per-skill `REVIEW_STATUS`, `DIFFERENTIATION`, and `REMOVAL PROPOSALS` parsing with an operator-decisions summary.

### Changed

- `scripts/auditing/SKILL_REVIEW_CHECKLIST.md` rewritten: process-predictability north star, named provenance, mandatory subtraction, differentiation as a reported flag, earned structure, imperative procedure steps.
- `scripts/auditing/SUBAGENT_REVIEW_PROCESS.md`: 7 quality gates, a removal-authority section, and `NO-CHANGE` as a verdict.
- `run_parallel_skill_reviews.sh` reviewer dispatch no longer forbids removal.
- `audit_skills.py`: `entry_over_200_lines` demoted from issue to warning.

### Removed

- `references/dot-agent`: a gitlink pinned at `0d2b562` with no `.gitmodules` entry.
- 3 vendored worker prompts in `subagent-orchestrator`: `code-quality-reviewer-prompt.md`, `implementer-prompt.md`, `spec-reviewer-prompt.md`.

### Fixed

- 11 repo-root script paths in 3 skills: `deps-audit`, `office-files`, `testing`.
- Stale `--skill python` example in `scripts/auditing/README.md` and `scripts/auditing/SUBAGENT_REVIEW_PROCESS.md`.

## 2026-08-01

### Removed

- 14 skills: `angular`, `dotnet-core`, `golang`, `javascript`, `nestjs`, `nextjs`, `nodejs`, `python`, `react`, `react-native`, `sql-querying`, `svelte`, `tailwind`, `typescript`.
