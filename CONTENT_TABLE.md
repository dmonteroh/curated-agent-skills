# Content Table

Total skills: 74

## Ai

| Skill | Summary |
| --- | --- |
| `agent-harness-portability` | Tests whether a skill or instruction corpus is harness-agnostic instead of merely asserting it: a per-target disposition pass over the axes on which agent harnesses differ, source-token leakage checks, and a defined repair for each failure. Use when authoring or auditing a portable skill, porting a corpus to another agent, or reviewing an untested portability claim. |
| `agent-memory-governance` | Governs memory an agent writes for its own future sessions — learnings, project notes, preference profiles, checkpoints — as a prompt-injection surface: quarantine-first trust tiers, human-gated global scope, provenance-gated writes, re-screening at load, and a capped retrieval budget. Use when designing, operating, or reviewing agent-authored memory. |
| `cdd-context` | Create and maintain CDD project context docs (product, tech stack, workflow) when setting up or updating docs/context, with optional scaffolding, indexing, validation, and a brief snapshot. |
| `context-budget` | Audits what an agent's standing instruction surface costs before any work starts: prices every always-loaded component, separates always-cost descriptions from on-demand bodies, classifies each as always, sometimes, or rarely needed, and ranks removals by tokens reclaimed. Use when context fills too fast, after adding capabilities, or before expanding a configuration. |
| `cross-vendor-delegation` | Provides the procedure for handing a bounded task to a model or agent running under another vendor's harness and adjudicating what comes back: content-not-path handoff, an injection-delimited payload, a bounded run whose stall stays diagnosable, a fail-closed verdict gate, and one comparative recommendation. Use when seeking an independent foreign-model opinion, or when a delegate's answer will gate a decision. |
| `google-stitch-ai` | Create DESIGN.md summaries from Google Stitch projects or offline assets for UI design workflows, and refine Stitch-ready UI prompts using extracted design tokens. |
| `mcp-server-development` | Build high-quality MCP (Model Context Protocol) servers: workflow-first tool design, tight schemas, predictable outputs, safe error handling, and eval-driven iteration. Framework-agnostic (Node/TS or Python). No web fetching required. |
| `prompt-engineering` | Designs, tests, and ships production prompts using prompt-as-code workflows: model-generation-aware patterns (reasoning controls, structured outputs, cache-friendly layout), templates, and evaluation guidance. Returns a full copy/paste prompt block. Use when building AI features, improving agent performance, adapting prompts to a new model or provider, porting an instruction set to another agent harness, or standardizing system prompts. |
| `skill-benchmark-harness` | Measures whether loading a skill changes what an agent produces: each eval prompt runs twice, with the skill and without, and both arms are graded blind against one id-stable assertion checklist. Reports the pass-rate delta, which assertions discriminate, and which regressed. Use when a skill's value rests on impression rather than measurement. |
| `subagent-orchestrator` | Decide whether and how to split work across subagents, then orchestrate execution safely with mode selection, claim-set and execution-surface control, barriered verification, and deterministic integration. |
| `tool-output-middleware` | Provides a design and verification procedure for a layer that rewrites tool output before it reaches an agent's context — compaction, filtering, redaction, summarization — without silently dropping the one line that mattered. Use when building or reviewing any such middleware. |

## Architecture

| Skill | Summary |
| --- | --- |
| `adr-madr-system` | Create, review, and maintain Architecture Decision Records (MADR) as individual files plus an ADR index when documenting or superseding architectural decisions. Focuses on decision drivers, options, consequences, and supersedes semantics so accepted ADRs remain immutable. |
| `architect-review` | Review system designs and major changes for architectural integrity, scalability, and maintainability; use for architecture decisions, tradeoffs, and risks across distributed systems and clean architecture patterns. |
| `backend-architect` | Guides backend architecture for operable services and APIs, covering boundaries, contracts, reliability, integration patterns, and rollout safety. Use when designing or changing backend services/APIs and their operability plans. |
| `monorepo-engineering` | Design and operate monorepos with clear boundaries, fast builds, and low-conflict collaboration. Covers workspace layout, dependency constraints, build caching, affected detection, versioning/publishing, and CI integration. Works standalone; choose tooling pragmatically (pnpm/yarn/npm, Nx/Turbo/Bazel). |
| `plan-review` | Reviews an implementation plan before any code is written: confirm the target, require alternatives beside the plan, set a scope posture (expand, cherry-pick, hold, cut), then audit architecture, code quality, tests, and performance. Every finding carries a confidence score and a quoted line of evidence, or it is suppressed. |

## Database

| Skill | Summary |
| --- | --- |
| `database-architect` | Design data layers and database architectures by selecting storage models, modeling schemas, and planning safe evolution with tradeoffs and migration/rollback plans. Use when making data-layer decisions or re-architecting storage. |
| `database-cost-optimization` | Reduce database infrastructure spend when costs need optimization by analyzing cost drivers, right-sizing compute/storage/replicas, and proposing verified rollback-ready changes without compromising reliability. |
| `database-migration-orm` | Plan and execute ORM-managed database migrations (Prisma/TypeORM/Sequelize/EF) with zero-downtime patterns, safe backfills, and rollback discipline. Use only for ORM migration tooling (not raw SQL-file migration workflows). |
| `database-migration-sql` | Plan and write forward-only SQL migration files with zero-downtime patterns, validation, rollback guidance, and production safety checks for PostgreSQL, MySQL, and SQL Server. |
| `database-performance` | Diagnose and fix database performance issues (slow queries, locks, pool saturation, caching, partitioning) using evidence from metrics and query plans. |
| `postgresql-engineering` | PostgreSQL-specific schema and data-layer engineering: DDL, data types, constraints, indexing, JSONB, partitioning, RLS, and safe schema evolution. Use when targeting Postgres specifically. |

## Design

| Skill | Summary |
| --- | --- |
| `frontend-design` | Implement distinctive, production-grade frontend UI code with high design quality. Use when asked to build or style components/pages/apps and deliver working UI code; avoid for design-only briefs without implementation. |
| `ui-design` | One canonical, framework-agnostic UI/UX design skill: turn requirements into clear UI briefs, flows, component specs, and design-system rules; review UI code against local guidelines; prioritize accessibility, consistency, and developer-hand-off clarity. Not a Google Stitch skill. |
| `ui-visual-validator` | Verifies UI changes via rigorous, evidence-based visual validation (screenshots/video/URLs) to catch regressions, design-system drift, responsive breakage, and visual accessibility issues; judges rendered UI against explicit criteria and screens separately for generic AI-generated design patterns. |

## Devops

| Skill | Summary |
| --- | --- |
| `cloud-architect` | Design cloud platform architecture (AWS/Azure/GCP): landing zones/accounts, networking, identity/IAM boundaries, service selection, reliability/DR, and multi-region strategy. Produces architecture diagrams + risk/rollback plans. Does not own CI/CD or deep FinOps tactics. |
| `cost-optimization` | Cloud FinOps cost governance for reducing cloud spend while maintaining reliability. Use when teams need tagging/chargeback, budgets/anomaly detection, rightsizing, commitment strategy (RIs/Savings Plans/CUDs), or unit-cost analysis. Produces a prioritized savings plan with verification gates. |
| `deployment-engineer` | Design and implement CI/CD and deployment automation: pipeline stages, quality gates, config validation, progressive delivery, rollback/runbooks, and GitOps patterns. Use for release workflows and deployment safety. Not for cloud platform architecture or deep IaC modules. |
| `devops-engineer` | Operate and evolve runtime infrastructure for reliability, containerization, Kubernetes operations, platform engineering, and operational readiness. Use for runtime reliability, deployment execution, or incident response prep; not for CI/CD pipeline architecture or release automation design. |
| `terraform-engineer` | Use when implementing infrastructure as code with Terraform across AWS, Azure, or GCP. Invoke for module development, state management, provider configuration, multi-environment workflows, infrastructure testing. |

## Docs

| Skill | Summary |
| --- | --- |
| `api-documenter` | Create or improve API documentation (OpenAPI, AsyncAPI, GraphQL) when developer-facing APIs need accurate docs, interactive references, and code examples. |
| `code-explain` | Explain complex code clearly for humans and agents. Produce a structured walkthrough (high-level intent -> data/control flow -> key invariants -> edge cases) with optional Mermaid diagrams and actionable next steps. Use for onboarding, debugging understanding, and “how it works” docs. |
| `doc-generate` | Generate and maintain high-signal documentation from an existing codebase (API docs, architecture, runbooks, onboarding, reverse-specs). Use when a repo needs structured, maintainable docs grounded in code and configuration. |
| `doc-sync` | Reconciles a repository's documentation against a change before it merges: audits every doc file against the branch diff, applies factual corrections without asking, escalates narrative and security edits, flags architecture-diagram drift without touching the diagram, and guards changelog entries and version bumps. Use when a branch is code-complete and its docs must match what shipped before review or merge. |
| `mermaid-expert` | Create Mermaid diagrams for flowcharts, sequences, ERDs, and architecture visuals with clear syntax, styling, and delivery guidance. |
| `office-files` | Work with Microsoft Office OOXML files (.docx/.pptx/.xlsx): inspect structure, extract text/tables, produce diffs, and generate clean Markdown summaries. Tool-agnostic and safe-by-default (prefers read-only workflows). Use when a task involves Word, PowerPoint, or Excel files. |
| `pdf-files` | Work with PDFs safely and repeatably: extract text/tables, convert pages to images, inspect/fill forms, and produce verifiable outputs (markdown/json/images/filled pdf). Use when a task involves PDF documents. |
| `prose-de-slopping` | Edits AI-generated prose into text that reads as human-written, using a catalogue of named tells with concrete replacements plus a guard that stops the pass from flattening legitimate writing. Use when a draft, doc, README, release note, or article reads as machine-written and has to ship. |
| `tutorial-engineer` | Creates step-by-step technical tutorials and onboarding guides from code or system requirements when teams need progressive, hands-on learning paths for developers. |

## Git

| Skill | Summary |
| --- | --- |
| `pr-description` | Generate a paste-ready pull request description from task briefs and the branch diff against a base branch. Produces three required sections — What & Why, How, Manual Verification Playbook — with change-type-aware playbook recipes. Use when a pull request body needs to be drafted or refreshed. |
| `smart-conventional-commits` | Create high-quality conventional commits from working-tree changes and user intent: inspect-first safe staging, repo-convention detection from git history, branch-aware type and scope inference, and strict title/body formatting. Use when users ask to commit changes or draft commit messages. |

## Observability

| Skill | Summary |
| --- | --- |
| `chaos-engineer` | Design and run safe chaos experiments (failure injection + game days) to validate resilience and reduce blast radius. Produces hypotheses, steady-state signals, rollback gates, and experiment specs. Use when resilience is uncertain or before high-risk changes. |
| `grafana-dashboards` | Provides guidance to create and manage production Grafana dashboards for real-time visualization of system and application metrics. Use when building monitoring dashboards, visualizing metrics, or creating operational observability interfaces. |
| `migration-observability` | Make database migrations safe and observable. Define progress + safety metrics, dashboards, and runbook gates (go/no-go criteria) for live migrations, backfills, and cutovers. Works standalone and is database/tooling agnostic. |
| `monitoring-expert` | Provides end-to-end observability across logs, metrics, traces, alerting, and performance testing. Use when instrumenting services, setting alert strategy, or designing an observability stack. |
| `performance` | End-to-end performance optimization workflow for baselining, profiling bottlenecks, proposing measurable fixes, and adding regression guardrails. Includes a safe-by-default scan/report script to capture repo signals and write a deterministic report. Use for latency/throughput/resource issues, scalability work, or performance gating. |
| `sre-engineer` | Site Reliability Engineering for production systems: define SLIs/SLOs and error budgets, design alerting and runbooks, reduce toil with automation, and improve incident response. Use when you need reliability targets and operational practices (not just dashboards). |

## Research

| Skill | Summary |
| --- | --- |
| `research-discipline` | Labels every claim in a research or investigation report as sourced, user-supplied, inferred, or a recommendation, escalates through sources lightest first, and dates freshness-sensitive findings. Use when reporting results from a lookup, investigation, comparison, or fact-finding task where the reader needs to tell verified fact from the agent's own inference. |
| `ux-interview` | Runs a structured UX user interview to capture current tasks, workflows, pain points, positives, and desired improvements. Use when the user asks to be interviewed about how they use a product, system, or process. |

## Security

| Skill | Summary |
| --- | --- |
| `auth-implementation-patterns` | Provides authentication and authorization implementation patterns (JWT, OAuth2/OIDC, sessions, RBAC) for designing, implementing, or reviewing secure access control in applications and APIs. |
| `deps-audit` | Produces a local, best-effort dependency audit summary and remediation plan for repos with dependency manifests. |
| `gdpr-data-handling` | Implement practical GDPR-compliant data handling (privacy by design, lawful basis, DSARs, retention, vendor/transfer controls, breach readiness). Use when building or reviewing systems that process EU personal data. |
| `pre-publication-sanitization` | Sanitization gate for taking a private repository public: six scan categories across the working tree and the full history, internal specifics replaced by documented placeholders rather than deleted, and a blocking gate held until each finding is resolved or overridden on the record. Use before a first public push or a visibility change. |
| `prompt-injection-defense` | Provides a layered prompt-injection defense procedure for agents that consume untrusted content — web pages, tool output, repository files, agent-authored notes. Covers ingress enumeration, normalizing before classifying, warn-versus-block policy, canary tripwires, fail-open ordering, and adversarial validation. Use when designing or reviewing an agent's trust boundaries. |
| `secrets-management` | Secure secrets handling for CI/CD, runtime, and local agent tooling: secret inventory, access boundaries, short-lived identity (OIDC/workload identity), rotation, leak response, egress control and audit receipts for data leaving a developer machine, and ambient-credential disambiguation. Works across Vault and cloud-native secret managers. |
| `security-auditor` | Provides a structured security audit workflow for DevSecOps, application security, and compliance readiness, used for scoped assessments, threat modeling, testing, remediation planning, trust-boundary siting of controls, and evidence-gated triage that suppresses false positives. |

## Workflow

| Skill | Summary |
| --- | --- |
| `adversarial-plan-review` | Hardens a proposal before committing to it: reviewers with distinct attack vectors file independent findings, cross-attack them, then defend, refine, or concede each one; only survivors are distilled into constraints, decisions, risks, and open questions. Use before large or irreversible work, when a plan reads plausible but unchallenged. |
| `agent-feedback-ui` | Collects a structured decision from a human out of band: generate a self-contained local page, spawn a one-shot HTTP server, block on a file result, then read typed data back. Covers transport, the handoff protocol, server state, page lifecycle after the server exits, and the degraded fallback. Use when the answer needs per-item ratings, notes, or visual comparison a prose prompt would flatten. |
| `brainstorming` | Clarify ambiguous work through structured brainstorming: ask focused questions, validate load-bearing premises as falsifiable claims, propose 2-3 approaches with tradeoffs, and produce a design brief (goals, non-goals, constraints, risks, validation) or a time-boxed spike note. Use when requirements are unclear or before large/irreversible changes. |
| `changelog-automation` | Automate changelog and release note generation from commits or PR metadata using Keep a Changelog and semantic versioning. Use when designing release workflows or standardizing commit conventions. |
| `cli-tools` | Build fast, user-friendly CLI tools with stable command surfaces, predictable output contracts (stdout vs stderr), and cross-platform behavior. Covers subcommands/flags, config precedence, interactive prompts, progress indicators, and shell completions. Use when designing or implementing CLI tools. |
| `code-review` | Provides high-signal, fast code review with selectable modes (quality, security, performance, tooling), triage of a third-party review bot's comments, an optional blind second-opinion pass, and stop conditions when the review applies its own fixes. Includes a safe-by-default script to scan diffs and produce a deterministic report. |
| `codify-exploration` | Promotes a repeated exploratory task into a deterministic, replayable on-disk unit: a written contract, a script with a pure parser, a frozen copy of its dependency, a dated fixture captured from the real source, and a test pinned to that fixture. Use when an exploration just succeeded and will be asked for again. |
| `daemon-lifecycle` | Adds a safe, supervisor-free singleton background daemon to a CLI tool: atomic state-file writes, an exclusive spawn lock with stale-holder reclaim, identity-verified process signaling, health-gated attach-vs-spawn decisions, and idle self-shutdown. Use when a CLI needs a persistent background process with no systemd, launchd, or container orchestrator supervising it, or when an existing one spawns duplicates, leaks processes, or has killed the wrong one. |
| `delivery-pipeline` | Sizes how much process one unit of work deserves using three independent signals, then runs only the phases that size earns, stopping for human approval before code is written and before commit. Use for one sequential change carried from request to commit: a new capability, a behavior change, a defect fix, a refactor, or an MVP bootstrapped from a spec. |
| `devex-review` | Reviews a proposed developer-facing product (API, CLI, SDK, library, platform, or its docs) for developer experience before it ships, distinct from reviewing its architecture or correctness. Investigates the target developer and their actual onboarding path for evidence before scoring, then rates DX per dimension on a calibrated 0-10 scale plus a separate time-to-first-result scale whose worst tier blocks rather than merely scoring low. Use on plans, design docs, or shipped products with a developer-facing surface. |
| `git-workflow` | Master Git workflows for teams: clean PRs, rebasing/merging, conflict resolution, cherry-picks, safe force-push, bisect, worktrees, and recovery via reflog. Includes playbooks + safe scripts for diagnosing and fixing common Git problems. |
| `interruption-budget` | Governs when an agent interrupts a human and how it decides the rest alone: classify every question as a one-way or two-way door where it is declared, never shrink an option set to fit a tool's cap, and shape each question to be answered fast and audited later. Use when about to ask a human, when options exceed a tool's cap, or when designing a workflow that asks repeatedly. |
| `jira-issue-management` | Create, read, transition, and link Jira issues (Epics, Tasks, Bugs) through an Atlassian MCP server, driven by a project-local Jira map file that caches cloud ID, status and transition IDs, account IDs, standing Epics, and conventions. Use when work involves creating or updating Jira tickets, turning a plan into Epics and Tasks, or bootstrapping the project's Jira map. |
| `refactor-clean` | Provides an incremental, test-first refactoring workflow for reducing complexity or duplication while keeping behavior stable, best used during technical-debt cleanup or design improvement. |
| `shell-scripting` | Write safe, portable shell scripts (POSIX sh or Bash) for automation, CI helpers, and command-line glue: shell selection, strict-mode setup with known caveats, quoting and cleanup patterns, and shellcheck-based verification. Use for scripting, tooling, and DevOps glue code. |
| `tech-debt` | Identify, quantify, and prioritize technical debt, then turn it into an executable remediation plan with ROI estimates, risk tiers, and verification steps. Use for debt audits, cleanup planning, or when velocity and quality are degrading. |
| `testing` | Create unit tests, API contract tests, and automation strategies for existing codebases with clear decision points, pitfalls, and deterministic reporting via local scripts. |
| `tracks-conductor-protocol` | Run a unified protocol for intake, task briefs, tracks (spec/plan), and execution with deterministic indexing, promotion (intake -> task -> track), and validation scripts. Use for structured work management aligned to SDD/CDD. |
