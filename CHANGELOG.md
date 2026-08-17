# Changelog

## 2026-08-17

### Removed

- `subagent-orchestrator`: the `## Worker Execution Surface` section of `SKILL.md`; its rules are carried in worked form by `references/worker-surface.md`.
- `subagent-orchestrator`: `references/agent-optimization.md`, with its pointers in `SKILL.md` and `references/README.md`.

### Added

- 21 skills: `agent-architecture-audit`, `agent-transaction-authority-security`, `brand-discovery`, `brand-voice`, `competitive-benchmark`, `customer-billing-ops`, `deterministic-extraction-gate`, `finetuning-method-selection`, `literature-review`, `living-docs-governance`, `loop-design-check`, `mle-workflow`, `network-change-review`, `network-device-diagnostics`, `network-segmentation-readiness`, `production-audit`, `recsys-pipeline-architect`, `root-cause-debugging`, `skill-corpus-maintenance`, `training-data-curation`, `ui-demo`.
- 3 categories: `business-operations`, `marketing`, `network`.
- 3 files in existing skills: `office-files/scripts/pptx_package_check.py`, `skill-benchmark-harness/references/behavioral-compliance.md`, `testing/references/flaky-test-triage.md`.
- 21 trigger-case files in `scripts/auditing/trigger-cases/`, one per skill added above; coverage is 95 of 95 skills.
- 19 skills: `adversarial-plan-review`, `agent-feedback-ui`, `agent-harness-portability`, `agent-memory-governance`, `codify-exploration`, `context-budget`, `cross-vendor-delegation`, `daemon-lifecycle`, `delivery-pipeline`, `devex-review`, `doc-sync`, `interruption-budget`, `plan-review`, `pre-publication-sanitization`, `prompt-injection-defense`, `prose-de-slopping`, `research-discipline`, `skill-benchmark-harness`, `tool-output-middleware`.
- 20 reference files across 14 skills: `api-documenter`, `cloud-architect`, `deployment-engineer`, `devops-engineer`, `doc-generate`, `frontend-design`, `grafana-dashboards`, `performance`, `postgresql-engineering`, `security-auditor`, `subagent-orchestrator`, `terraform-engineer`, `ui-design`, `ui-visual-validator`.
- 19 trigger-case files in `scripts/auditing/trigger-cases/`, one per skill added above; coverage is now 74 of 74 skills.
- `scripts/auditing/proposals.py`, with `scripts/auditing/PROPOSALS.md` (pending-rulings ledger) and `scripts/auditing/apply-prompt.md` (writer prompt): removal-ruling loop — `record` appends review proposals to the ledger, `lint` validates rulings and checksums, `apply` executes `approved`/`declined` rulings via a scoped writer dispatch and records them in `scripts/auditing/OPEN_ITEMS.md`.
- `scripts/tests/test_proposals.py`: tests for the ruling loop.

### Changed

- 26 skills absorbed techniques from the NEW-list evaluation: `agent-memory-governance`, `backend-architect`, `cdd-context`, `cloud-architect`, `codify-exploration`, `context-budget`, `cross-vendor-delegation`, `database-migration-sql`, `database-performance`, `delivery-pipeline`, `deployment-engineer`, `doc-generate`, `frontend-design`, `office-files`, `performance`, `prompt-engineering`, `prompt-injection-defense`, `prose-de-slopping`, `refactor-clean`, `research-discipline`, `security-auditor`, `skill-benchmark-harness`, `sre-engineer`, `testing`, `ui-design`, `ux-interview`.
- `ux-interview` scope narrowed to producing an interaction spec; saturation stop criterion added.
- `skill-benchmark-harness` stand-down widened: a tool-call trace counts as a durable artifact.
- Frontmatter descriptions: `skill-benchmark-harness`, `ux-interview`.
- 20 skills absorbed extracted techniques: `adr-madr-system`, `architect-review`, `auth-implementation-patterns`, `brainstorming`, `cli-tools`, `code-review`, `deployment-engineer`, `doc-generate`, `git-workflow`, `mcp-server-development`, `mermaid-expert`, `prompt-engineering`, `refactor-clean`, `secrets-management`, `security-auditor`, `subagent-orchestrator`, `testing`, `tutorial-engineer`, `ui-design`, `ui-visual-validator`.
- 33 skills absorbed techniques from the MERGE-list evaluation: `adr-madr-system`, `api-documenter`, `architect-review`, `backend-architect`, `brainstorming`, `cdd-context`, `cloud-architect`, `code-review`, `database-architect`, `database-migration-sql`, `database-performance`, `deployment-engineer`, `devops-engineer`, `doc-generate`, `frontend-design`, `gdpr-data-handling`, `git-workflow`, `grafana-dashboards`, `mcp-server-development`, `monitoring-expert`, `monorepo-engineering`, `performance`, `postgresql-engineering`, `prompt-engineering`, `refactor-clean`, `security-auditor`, `shell-scripting`, `subagent-orchestrator`, `terraform-engineer`, `testing`, `tracks-conductor-protocol`, `ui-design`, `ui-visual-validator`.
- 26 trigger-case files extended for skills whose activation scope widened: `adr-madr-system`, `architect-review`, `backend-architect`, `cdd-context`, `cloud-architect`, `code-review`, `database-architect`, `deployment-engineer`, `devops-engineer`, `doc-generate`, `frontend-design`, `git-workflow`, `grafana-dashboards`, `monitoring-expert`, `performance`, `postgresql-engineering`, `prompt-engineering`, `refactor-clean`, `security-auditor`, `shell-scripting`, `subagent-orchestrator`, `terraform-engineer`, `testing`, `tracks-conductor-protocol`, `ui-design`, `ui-visual-validator`.
- Frontmatter descriptions: `cdd-context`, `cloud-architect`, `performance`, `terraform-engineer`.
- `CONTENT_TABLE.md` regenerated.
- `scripts/auditing/review-result.sh` writes the `--removals` text verbatim to `$REVIEW_REMOVALS_FILE` when that variable is set; `scripts/auditing/run_parallel_skill_reviews.sh` sets it on the synthesis call and runs `proposals.py record` after a pass with proposals.
- `scripts/auditing/synthesis-prompt.md`: the `--removals` argument carries the removal-proposals block verbatim.
- `scripts/auditing/run_parallel_skill_reviews.sh`: reviewer arms run at `medium` reasoning effort by default, overridable with `--effort` (claude arm via `--effort`, codex arm via `-c model_reasoning_effort`); `--synthesis-effort` sets the synthesis call's effort (default unset); the codex arm pins `-c service_tier=default`.
- `scripts/auditing/reviewer-prompt.md`, `scripts/auditing/synthesis-prompt.md`, `scripts/auditing/apply-prompt.md`, `scripts/auditing/run_parallel_skill_reviews.sh`, `scripts/auditing/proposals.py`: dispatched calls carry a session-bootstrap exemption (a `Dispatch context:` preamble in all three prompt assets; claude calls also append it via `--append-system-prompt`).

### Fixed

- `ui-design`: `useAnnounce` ignored its `priority` argument, so assertive announcements rendered as polite; `Announcer` was declared inside the hook body and remounted on every render.
- `ui-design`: accessible-button pattern set both `disabled` and `aria-disabled`, and cited a Level AAA touch-target size while claiming Level AA conformance.
- `ui-design`: `commands/accessibility-audit.md` contradicted itself on 44px and 24px touch targets, and defaulted to WCAG 2.1 while carrying WCAG 2.2 criteria.
- `ui-design`: WCAG SC 2.4.11 Focus Not Obscured (Minimum), Level AA, added to the criteria table, guidelines reference, audit checklist, and pre-review gate.
- `office-files`: `scripts/ooxml_extract.py` ordered slides by filename instead of resolving the presentation relationship graph; adds `slide_order_source`.
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
