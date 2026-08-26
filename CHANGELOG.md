# Changelog

## 2026-08-26

### Added

- `writing-style`: skill, `references/README.md`, `references/writing-guide.md`, `references/always-on-block.md`, `scripts/writing_lint.py`, `scripts/tests/test_writing_lint.py`, `scripts/tests/mutation_check.py`, and `scripts/auditing/trigger-cases/writing-style.md`.
- `writing-style`: 14 linter rules in `scripts/writing_lint.py` — `L15` negation pivot, `L16` signposting, `L17` unevidenced superlative, `L18` emoji, `A11` rhetorical-question opener, `A12` over-formatted reply, `A13` bold-label bullet cluster, `A14` copula avoidance, `A15` noun stack, `A16` pseudo-analytic participle tail, `A17` false range, `A18` engagement-farming close, `A19` generic positive conclusion, `A20` abstract-register cluster; 25 fixtures in `scripts/tests/test_writing_lint.py` and 16 mutants in `scripts/tests/mutation_check.py`.

### Changed

- `writing-style`: `SKILL.md` carries 12 numbered rules, adding the negation pivot, signposting, and emoji; the deliverable-only carve-out reads "apply rules 1 to 10". The same three rules are in `references/always-on-block.md`.
- `writing-style`: `A12` disabled in the `instruction`, `documentation` and `report` profiles; `A18` disabled in `conversation`.
- `writing-style`: `HYPE_ADVISORY` in `scripts/writing_lint.py` extended with the post-2023 abstract register, and a `LITERAL_SENSE` table exempts the construction sense of `load-bearing` and the orientation sense of `landscape`. `STACK_NOUNS` and `POSITIVE_CLOSE` rebuilt so `A15` and `A19` detect the patterns they name. `SKILL.md` Provenance names `conorbronsdon/avoid-ai-writing` (MIT) and records that no frequency claim is carried from it.

### Removed

- `writing-style`: the `--config` flag and its `dash_policy`, `profiles`, `extra_banned` and `allow` keys from `scripts/writing_lint.py`, with the matching sections of `SKILL.md`, `references/writing-guide.md` and `references/README.md`, and four fixtures. `DASH_POLICY` remains as a module constant.
- `writing-style`: the machine-written stand-down bullet from `SKILL.md`, `## Do not use this skill when`.


## 2026-08-23

### Changed

- `scripts/auditing/SKILL_REVIEW_CHECKLIST.md` (preamble, Verdicts) and `scripts/auditing/SUBAGENT_REVIEW_PROCESS.md` (Quality Gate 7): ruled ground cites `scripts/auditing/logs/removal-rulings.md`; parity-register pointers in `scripts/auditing/SUBAGENT_REVIEW_PROCESS.md`, `scripts/auditing/references/authoring-guidance.md`, `scripts/audit_skills.py`, and `scripts/check_parity.py` cite the families declared in `scripts/check_parity.py`.

### Removed

- `scripts/auditing/OPEN_ITEMS.md`, and every reference to it: the `OPEN_ITEMS_PATH` plumbing in `scripts/auditing/run_parallel_skill_reviews.sh`, its read-first bullets in `scripts/auditing/reviewer-prompt.md` and `scripts/auditing/synthesis-prompt.md`, its `scripts/auditing/README.md` entry and placeholder-list mentions, comment/docstring citations in `scripts/auditing/proposals.py`, and its fixtures in `scripts/tests/test_proposals.py` and `scripts/tests/test_reviewer_prompt_asset.py`.
- `scripts/auditing/PROPOSALS.md`: entry `bc26a53d3a02`, ruling recorded in `scripts/auditing/logs/removal-rulings.md`.

## 2026-08-22

### Changed

- `scripts/auditing/proposals.py`: `apply` writes executed and declined removal rulings to `scripts/auditing/logs/removal-rulings.md`, creating it when absent, and `record` dedupes ruled ids against that file; the 236 existing rulings moved there out of `scripts/auditing/OPEN_ITEMS.md`. `scripts/auditing/README.md` and `scripts/auditing/SUBAGENT_REVIEW_PROCESS.md` updated.

- `subagent-orchestrator`: activation gate split into entry and dispatch checks; task-board rows added for the human gate and the runtime probe result; `QUESTIONS` handling added to step 4; unbounded review-loop trigger added to the use boundary; never-parallel summary aligned with `references/claim-sets.md`.
- `subagent-orchestrator`: worker packet gains execution-surface and controller-run verification fields, a validator-task carve-out on the no-verification constraint, and an untrusted-context end terminator; reviewer packet no longer carries the round number; fix packet gains a controller-read gate on forwarded findings.
- `subagent-orchestrator`: both runtime adapters switch dispatch examples to stdin/file packet delivery and document worker skill-layer controls (`--disallowedTools "Skill"`, `CLAUDE_CONFIG_DIR`, `CODEX_HOME`), `claude --json-schema`, native-subagent model/effort overrides and the continuation hazard, and `codex exec --approve-for-me`.
- `subagent-orchestrator`: mode guides gain execution-surface fields, worker-started-process barrier checks, and review-convergence pointers; `references/README.md` load rule and adapter descriptions refreshed.
- `subagent-orchestrator`: Hard Invariant 3 restated as surface-based — with per-task worktrees and disjoint claims a finished task may be verified while siblings run; without that isolation, verification waits for the global barrier. Step 5, `references/execution-true-parallel.md`, and `references/runtime-claude.md` carry the same rule.
- `subagent-orchestrator`: workers may self-check inside their granted surfaces and report outcomes as evidence; the controller's post-barrier verification stays the gate. Worker and fix packets in `references/packet-templates.md` carry the rule and a `Self-checks run` deliverable line.
- `subagent-orchestrator`: symmetric effort policy — worker effort defaults to `medium` on every vendor, above-`medium` only under stated operator authorization, never by interrupting a run. Stated in `SKILL.md` Required inputs; both runtime adapters pin `medium` in their examples, and the Claude adapter notes the flag must be passed explicitly since its vendor default is `high`.
- `postgresql-engineering`: schema-enforced optimistic-concurrency pattern (`UNIQUE (entity_id, version)`, with SQL example and two-writer verification) in `references/indexing-and-constraints.md`, a Workflow step-2 decision line, and its `references/README.md` index line.
- `monitoring-expert`: Workflow steps 2, 4, and 5 carry the correlation-ID, sensitive-field-redaction, health-check, trace-sampling, dashboard-audience, business-KPI, alert-fatigue, and runbook-link rules; Example 1 carries exemplar, baseline-delta, and end-to-end verification lines.
- `devops-engineer`: `## Decision points` bullets 1-3 condensed to their decision cue plus the `references/kubernetes-workload-safety.md` pointer.
- `scripts/auditing/references/authoring-guidance.md`: the worked differentiation contrast cites measured with/without verdicts.
- `CODEX_SKILLS_SYNC.md`: database bundle example updated.
- `CONTENT_TABLE.md` regenerated; `scripts/auditing/skills_list.txt` and `scripts/tests/data/audit_snapshot.json` updated.

### Removed

- `database-architect`: the whole skill (`SKILL.md`, `references/README.md`, `references/migration-safety.md`, `references/modeling-checklist.md`, `references/tech-selection.md`) and `scripts/auditing/trigger-cases/database-architect.md`.
- `cloud-architect`: the `## Common pitfalls` section of `SKILL.md`.
- `monitoring-expert`: the `## Constraints` and `## Common pitfalls` sections of `SKILL.md`.
- `subagent-orchestrator`: `references/execution-modes.md`, with its pointers in `SKILL.md` and `references/README.md`.
- `subagent-orchestrator`: `references/execution-prompt-parallel.md`; the `prompt-parallel` mode is collapsed into `queued-serial`, which absorbs its two decision points; mode lists in `SKILL.md`, `references/README.md`, `references/runtime-claude.md`, and `references/runtime-codex.md` updated.
- `subagent-orchestrator`: the `## Common pitfalls` section of `SKILL.md`.
- `subagent-orchestrator`: all dot-agent content — the step-1 load-order list, the `### 8) Optional dot-agent Maintenance` section, the Output-contract line, the Final Report Template block in `references/packet-templates.md`, and the step-5 line in `references/execution-single-worker.md`.

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
