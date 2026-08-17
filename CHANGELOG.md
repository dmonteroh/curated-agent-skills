# Changelog

## 2026-08-17

### Added

- 19 skills: `adversarial-plan-review`, `agent-feedback-ui`, `agent-harness-portability`, `agent-memory-governance`, `codify-exploration`, `context-budget`, `cross-vendor-delegation`, `daemon-lifecycle`, `delivery-pipeline`, `devex-review`, `doc-sync`, `interruption-budget`, `plan-review`, `pre-publication-sanitization`, `prompt-injection-defense`, `prose-de-slopping`, `research-discipline`, `skill-benchmark-harness`, `tool-output-middleware`.
- 20 reference files across 14 skills: `api-documenter`, `cloud-architect`, `deployment-engineer`, `devops-engineer`, `doc-generate`, `frontend-design`, `grafana-dashboards`, `performance`, `postgresql-engineering`, `security-auditor`, `subagent-orchestrator`, `terraform-engineer`, `ui-design`, `ui-visual-validator`.
- 19 trigger-case files in `scripts/auditing/trigger-cases/`, one per skill added above; coverage is now 74 of 74 skills.

### Changed

- 20 skills absorbed extracted techniques: `adr-madr-system`, `architect-review`, `auth-implementation-patterns`, `brainstorming`, `cli-tools`, `code-review`, `deployment-engineer`, `doc-generate`, `git-workflow`, `mcp-server-development`, `mermaid-expert`, `prompt-engineering`, `refactor-clean`, `secrets-management`, `security-auditor`, `subagent-orchestrator`, `testing`, `tutorial-engineer`, `ui-design`, `ui-visual-validator`.
- 33 skills absorbed techniques from the MERGE-list evaluation: `adr-madr-system`, `api-documenter`, `architect-review`, `backend-architect`, `brainstorming`, `cdd-context`, `cloud-architect`, `code-review`, `database-architect`, `database-migration-sql`, `database-performance`, `deployment-engineer`, `devops-engineer`, `doc-generate`, `frontend-design`, `gdpr-data-handling`, `git-workflow`, `grafana-dashboards`, `mcp-server-development`, `monitoring-expert`, `monorepo-engineering`, `performance`, `postgresql-engineering`, `prompt-engineering`, `refactor-clean`, `security-auditor`, `shell-scripting`, `subagent-orchestrator`, `terraform-engineer`, `testing`, `tracks-conductor-protocol`, `ui-design`, `ui-visual-validator`.
- 26 trigger-case files extended for skills whose activation scope widened: `adr-madr-system`, `architect-review`, `backend-architect`, `cdd-context`, `cloud-architect`, `code-review`, `database-architect`, `deployment-engineer`, `devops-engineer`, `doc-generate`, `frontend-design`, `git-workflow`, `grafana-dashboards`, `monitoring-expert`, `performance`, `postgresql-engineering`, `prompt-engineering`, `refactor-clean`, `security-auditor`, `shell-scripting`, `subagent-orchestrator`, `terraform-engineer`, `testing`, `tracks-conductor-protocol`, `ui-design`, `ui-visual-validator`.
- Frontmatter descriptions: `cdd-context`, `cloud-architect`, `performance`, `terraform-engineer`.
- `CONTENT_TABLE.md` regenerated.

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
