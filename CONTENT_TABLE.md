# Content Table

Total skills: 94

## Ai

| Skill | Summary |
| --- | --- |
| `agent-architecture-audit` | Diagnoses an agent or LLM application whose behavior degraded when the failing layer is unknown: triages the stack layer by layer, records every finding against exactly one layer with a resolvable evidence reference and an evidence grade, ranks by severity, and orders fixes so enforcement moves into code before any prompt is rewritten. Use when the symptom is reported and the cause is not located. |
| `agent-harness-portability` | Tests whether a skill or instruction corpus is harness-agnostic instead of merely asserting it: a per-target disposition pass over the axes on which agent harnesses differ, source-token leakage checks, and a defined repair for each failure. Use when authoring or auditing a portable skill, porting a corpus to another agent, or reviewing an untested portability claim. |
| `agent-memory-governance` | Governs memory an agent writes for its own future sessions — learnings, project notes, preference profiles, checkpoints — as a prompt-injection surface: quarantine-first trust tiers, human-gated global scope, provenance-gated writes, re-screening at load, and a capped retrieval budget. Use when designing, operating, or reviewing agent-authored memory. |
| `cdd-context` | Create and maintain CDD project context docs (product, tech stack, workflow, optional product guidelines) when setting up or updating docs/context, with optional scaffolding, brownfield extraction from an existing codebase, indexing, validation, and a brief snapshot. |
| `context-budget` | Audits what an agent's standing instruction surface costs before any work starts: prices every always-loaded component, separates always-cost descriptions from on-demand bodies, classifies each as always, sometimes, or rarely needed, and ranks removals by tokens reclaimed. Use when context fills too fast, after adding capabilities, or before expanding a configuration. |
| `cross-vendor-delegation` | Provides the procedure for handing a bounded task to a model or agent running under another vendor's harness and adjudicating what comes back: content-not-path handoff, an injection-delimited payload, a bounded run whose stall stays diagnosable, a fail-closed verdict gate, and one comparative recommendation. Use when seeking an independent foreign-model opinion, or when a delegate's answer will gate a decision. |
| `deterministic-extraction-gate` | Decides whether a model belongs in a text-extraction loop at all, then builds the seam: a deterministic parser that accounts for every region of its input, reason-code flags rather than a confidence score, escalation of flagged records only, and a labelled sample that measures the miss rate. Use when extracting fields from many similarly shaped records. |
| `finetuning-method-selection` | Routes a fine-tuning request by the data shape actually in hand — demonstrations, preference pairs, unpaired feedback, or a checkable pass/fail — then clears that branch's precondition gate before a run is configured. Use when scoping a training effort, or when it is unclear whether training is the right tool at all. |
| `google-stitch-ai` | Create DESIGN.md summaries from Google Stitch projects or offline assets for UI design workflows, and refine Stitch-ready UI prompts using extracted design tokens. |
| `loop-design-check` | Designs an autonomous agent loop and reviews an existing one for the ways loops fail: spinning on a goal no machine can settle, gaming the verifier, or running a wrong answer to completion. Gates whether the loop is deserved, pairs a done-criterion with a boundary, picks a control shape and skeleton, and adds damping. Use before building a repeating unattended run, or when one already exists and might run away. |
| `mcp-server-development` | Build high-quality MCP (Model Context Protocol) servers: workflow-first tool design, tight schemas, predictable outputs, safe error handling, and eval-driven iteration. Framework-agnostic (Node/TS or Python). No web fetching required. |
| `mle-workflow` | Takes a trained model to production: a prediction contract and a data contract written before model code, a pipeline another engineer can rerun, promotion gates declared before training finishes and failing closed on a missing metric, a serving path with a proven train-serve equivalence test, and drift signals with a rollback artifact once live. Use when a model has to become a system. |
| `prompt-engineering` | Designs, tests, and ships production prompts using prompt-as-code workflows: model-generation-aware patterns (reasoning controls, structured outputs, cache-friendly layout), templates, and evaluation guidance. Returns a full copy/paste prompt block. Use when building AI features, improving agent performance, adapting prompts to a new model or provider, porting an instruction set to another agent harness, or standardizing system prompts. |
| `skill-benchmark-harness` | Measures what one change does to agent behavior: each eval prompt runs twice under one arm variable — the skill loaded or absent, or one agent against another — both arms graded blind against one id-stable assertion checklist. Reports the pass-rate delta, which assertions discriminate, and which regressed. Use when the case for a skill or an agent rests on impression rather than measurement. |
| `skill-corpus-maintenance` | Grooming pass over an agent's own instruction corpus: one deterministic inventory feeds a keep/revise/retire verdict per item and the promotion of recurring principles into the standing rule text. Batched cross-reads, evidence-bearing reasons, approval before any mutation, and a dated record so the next run re-evaluates only what changed. Use for periodic maintenance, not author-time review. |
| `subagent-orchestrator` | Decide whether and how to split work across subagents, then orchestrate execution safely with mode selection, claim-set and execution-surface control, barriered verification, and deterministic integration. |
| `tool-output-middleware` | Provides a design and verification procedure for a layer that rewrites tool output before it reaches an agent's context — compaction, filtering, redaction, summarization — without silently dropping the one line that mattered. Use when building or reviewing any such middleware. |
| `training-data-curation` | Turns graded examples and traces into a training set: selects which rows earn a place, holds evaluation items out by identifier at the one seam where that is still possible, shapes rows to the target method, masks loss to response spans, and emits a provenance card that gates the run. Use when building or auditing training data. |

## Architecture

| Skill | Summary |
| --- | --- |
| `adr-madr-system` | Create, review, and maintain Architecture Decision Records (MADR) as individual files plus an ADR index when documenting or superseding architectural decisions. Focuses on decision drivers, options, consequences, and supersedes semantics so accepted ADRs remain immutable. |
| `architect-review` | Review system designs and major changes for architectural integrity, scalability, and maintainability; use for architecture decisions, tradeoffs, and risks across distributed systems and clean architecture patterns. |
| `backend-architect` | Guides backend architecture for operable services and APIs, covering boundaries, contracts, reliability, integration patterns, and rollout safety. Use when designing or changing backend services/APIs and their operability plans. |
| `monorepo-engineering` | Design and operate monorepos with clear boundaries, fast builds, and low-conflict collaboration. Covers workspace layout, dependency constraints, build caching, affected detection, versioning/publishing, and CI integration. Works standalone; choose tooling pragmatically (pnpm/yarn/npm, Nx/Turbo/Bazel). |
| `plan-review` | Reviews an implementation plan before any code is written: confirm the target, require alternatives beside the plan, set a scope posture (expand, cherry-pick, hold, cut), then audit architecture, code quality, tests, and performance. Every finding carries a confidence score and a quoted line of evidence, or it is suppressed. |
| `recsys-pipeline-architect` | Designs the stages around a scorer for systems that pick the top K items for a subject and context - feeds, recommenders, notification digests, task prioritizers - as an ordered source, hydrate, filter, score, select, side-effect pipeline. Use when structuring or decomposing ranking plumbing, not when changing what a retriever returns. |

## Business Operations

| Skill | Summary |
| --- | --- |
| `customer-billing-ops` | Resolves one named customer's billing problem: fixes identity to a single account, classifies the case into one of five buckets against stated observables, acts in reversibility order so money moves last, and hands off a fixed record naming the product gap behind the ticket. Use for live customer billing operations — duplicate charges, failed renewals, refund requests, cancellations with no self-serve path. |

## Database

| Skill | Summary |
| --- | --- |
| `database-cost-optimization` | Reduce database infrastructure spend when costs need optimization by analyzing cost drivers, right-sizing compute/storage/replicas, and proposing verified rollback-ready changes without compromising reliability. |
| `database-migration-orm` | Plans and executes ORM-managed database migrations (Prisma/TypeORM/Sequelize/EF) with zero-downtime patterns, safe backfills, and rollback discipline. Use only for ORM migration tooling (not raw SQL-file migration workflows). |
| `database-migration-sql` | Plan and write forward-only SQL migration files with zero-downtime patterns, validation, rollback guidance, and production safety checks for PostgreSQL, MySQL, and SQL Server. |
| `database-performance` | Diagnoses and fixes database performance issues — slow queries, lock contention, pool saturation, caching, partitioning — using evidence from metrics and query plans. Use when a latency or throughput regression traces to the database layer. |
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
| `cloud-architect` | Designs cloud platform architecture (AWS/Azure/GCP) when a system is being designed for cloud, migrated to it, or connected to on-premises networks: landing zones/accounts, networking, hybrid on-prem connectivity, identity/IAM boundaries, service selection, reliability/DR, and multi-region strategy. Produces architecture diagrams + risk/rollback plans. Does not own CI/CD or deep FinOps tactics. |
| `cost-optimization` | Cloud FinOps cost governance for reducing cloud spend while maintaining reliability. Use when teams need tagging/chargeback, budgets/anomaly detection, rightsizing, commitment strategy (RIs/Savings Plans/CUDs), or unit-cost analysis. Produces a prioritized savings plan with verification gates. |
| `deployment-engineer` | Design and implement CI/CD and deployment automation: pipeline stages, quality gates, config validation, progressive delivery, rollback/runbooks, and GitOps patterns. Use for release workflows and deployment safety. Not for cloud platform architecture or deep IaC modules. |
| `devops-engineer` | Operate and evolve runtime infrastructure for reliability, containerization, Kubernetes operations, platform engineering, and operational readiness. Use for runtime reliability, deployment execution, or incident response prep; not for CI/CD pipeline architecture or release automation design. |
| `production-audit` | Produces a ship-or-block readiness verdict for one repository from local, user-authorized evidence only, naming both the evidence checked and the evidence missing. Use when asked whether an application is ready to ship, what would break in production, or what must be fixed before a launch. |
| `terraform-engineer` | Use when implementing infrastructure as code with Terraform across AWS, Azure, GCP, or OCI. Invoke for module development, state management, provider configuration, multi-environment workflows, infrastructure testing. |

## Docs

| Skill | Summary |
| --- | --- |
| `api-documenter` | Create or improve API documentation (OpenAPI, AsyncAPI, GraphQL) when developer-facing APIs need accurate docs, interactive references, and code examples. |
| `code-explain` | Explain complex code clearly for humans and agents. Produce a structured walkthrough (high-level intent -> data/control flow -> key invariants -> edge cases) with optional Mermaid diagrams and actionable next steps. Use for onboarding, debugging understanding, and “how it works” docs. |
| `doc-generate` | Generate and maintain high-signal documentation from an existing codebase (API docs, architecture, runbooks, onboarding, reverse-specs). Use when a repo needs structured, maintainable docs grounded in code and configuration. |
| `doc-sync` | Reconciles a repository's documentation against a change before it merges: audits every doc file against the branch diff, applies factual corrections without asking, escalates narrative and security edits, flags architecture-diagram drift without touching the diagram, and guards changelog entries and version bumps. Use when a branch is code-complete and its docs must match what shipped before review or merge. |
| `living-docs-governance` | Assigns four maintenance roles — rules, map, status, history — across the documentation a repository already has, so every fact has exactly one owner and each later change updates exactly one role. Use when a long-lived project's docs drift from its code, deleted paths keep being recreated, or every session re-derives context that is supposed to be written down. |
| `mermaid-expert` | Create Mermaid diagrams for flowcharts, sequences, ERDs, and architecture visuals with clear syntax, styling, and delivery guidance. Use when Mermaid diagram code, diagram type selection, or delivery guidance is needed. |
| `office-files` | Works with Microsoft Office OOXML files (.docx/.pptx/.xlsx): inspects structure, extracts text/tables, produces diffs, and generates clean Markdown summaries. Tool-agnostic and safe-by-default (prefers read-only workflows). Use when a task involves Word, PowerPoint, or Excel files. |
| `pdf-files` | Work with PDFs safely and repeatably: extract text/tables, convert pages to images, inspect/fill forms, and produce verifiable outputs (markdown/json/images/filled pdf). Use when a task involves PDF documents. |
| `prose-de-slopping` | Edits AI-generated prose into text that reads as human-written, using a catalogue of named tells with concrete replacements plus a guard that stops the pass from flattening legitimate writing. Use when a draft, doc, README, release note, or article reads as machine-written and has to ship. |
| `tutorial-engineer` | Creates step-by-step technical tutorials and onboarding guides from code or system requirements when teams need progressive, hands-on learning paths for developers. |
| `ui-demo` | Produces a walkthrough recording of a running web application through a fixed discover, rehearse, record sequence, with a rehearsal gate that blocks recording until every selector resolves. Use when a demo video, screen recording, walkthrough or tutorial capture is requested; not for checking whether the UI is correct. |

## Git

| Skill | Summary |
| --- | --- |
| `pr-description` | Generates a paste-ready pull request description from task briefs and the branch diff against a base branch. Produces three required sections — What & Why, How, Manual Verification Playbook — with change-type-aware playbook recipes. Use when a pull request body needs to be drafted or refreshed. |
| `smart-conventional-commits` | Create high-quality conventional commits from working-tree changes and user intent: inspect-first safe staging, repo-convention detection from git history, branch-aware type and scope inference, and strict title/body formatting. Use when users ask to commit changes or draft commit messages. |

## Marketing

| Skill | Summary |
| --- | --- |
| `brand-discovery` | Runs a brand identity interview across several sessions: one question per turn, captured to disk after every section, and checkpointed so a later session resumes where the last one stopped. Interviews multiple stakeholders separately and reconciles them afterwards. Produces a written identity reference that designers, writers, and outside collaborators can be briefed from. Use when a brand's identity is being created, repositioned, or made explicit across multiple sessions or stakeholders. |
| `brand-voice` | Derives a reusable writing-voice profile from an author's or brand's real published material — posts, essays, memos, outbound that worked, product copy — and emits it as a named block later drafting can load instead of re-deriving style. Use when written output has to sound like a specific person or brand and real samples exist to derive it from. |

## Network

| Skill | Summary |
| --- | --- |
| `network-change-review` | Reviews a candidate router or switch configuration before it is pushed, by hand or by automation. Checks destructive commands, credential and management-plane exposure, address collisions, stale references, and hygiene, then gates the change window. Use before a network config reaches a device. |
| `network-device-diagnostics` | Triages a live router, switch, or host link read-only: BGP session state, route exchange, interface errors, drops, and duplex or speed mismatches. Produces an evidence record, not a fix. Use when a network device is misbehaving now and every mutating action must wait for a change window. |
| `network-segmentation-readiness` | Gates a restructure of a small network before any command is issued: trust zones, local DNS resolver placement, and remote access. Collects inventory, proves management access survives, and stages the migration. Use when splitting a flat network, moving DHCP to a local resolver, or adding VPN access. |

## Observability

| Skill | Summary |
| --- | --- |
| `chaos-engineer` | Design and run safe chaos experiments (failure injection + game days) to validate resilience and reduce blast radius. Produces hypotheses, steady-state signals, rollback gates, and experiment specs. Use when resilience is uncertain or before high-risk changes. |
| `grafana-dashboards` | Provides guidance to create and manage production Grafana dashboards for real-time visualization of system and application metrics. Use when building monitoring dashboards, visualizing metrics, or creating operational observability interfaces. |
| `migration-observability` | Makes database migrations safe and observable. Defines progress and safety metrics, dashboards, and runbook gates (go/no-go criteria) for live migrations, backfills, and cutovers. Works standalone and is database/tooling agnostic. |
| `monitoring-expert` | Provides end-to-end observability across logs, metrics, traces, alerting, and performance testing. Use when instrumenting services, setting alert strategy, or designing an observability stack. |
| `performance` | End-to-end performance optimization workflow for baselining, profiling bottlenecks, proposing measurable fixes, and adding regression guardrails. Includes a safe-by-default scan/report script to capture repo signals and write a deterministic report. Use for latency/throughput/resource issues, data freshness, build-loop timing, scalability work, or performance gating. |
| `sre-engineer` | Site Reliability Engineering for production systems: define SLIs/SLOs and error budgets, design alerting and runbooks, reduce toil with automation, and improve incident response. Use when you need reliability targets and operational practices (not just dashboards). |

## Research

| Skill | Summary |
| --- | --- |
| `competitive-benchmark` | Runs a competitive positioning benchmark as one pipeline: elicits the client's positioning brief, scopes and tiers a candidate set, scores every survivor on fixed dimensions with evidence per score, then assembles a decision-grade report. Emits no composite score and never averages the poles of the client's strategic tension. Use when a named organization needs a defensible read of the rivals contesting its position. |
| `literature-review` | Takes a research question through one reproducible pass over a body of academic or technical literature — protocol before collection, logged searches, deduplication, staged screening with recorded exclusions, per-study methodological appraisal, and confidence-tiered synthesis. Use when a corpus has to be found, screened, appraised, and cited rather than a single answer looked up. |
| `research-discipline` | Labels every claim in a research or investigation report as sourced, user-supplied, inferred, or a recommendation, escalates through sources lightest first, and dates freshness-sensitive findings. Use when reporting results from a lookup, investigation, comparison, or fact-finding task where the reader needs to tell verified fact from the agent's own inference. |
| `ux-interview` | Interviews a user about how they work today and produces an interaction spec: required product behaviors traced to observed usage, saved with the transcript that evidences them. Use when a product spec or an interaction design needs grounding in real usage rather than assumption. |

## Security

| Skill | Summary |
| --- | --- |
| `agent-transaction-authority-security` | Provides a layered control procedure for autonomous agents that can move value — trades, swaps, transfers, treasury operations — with every limit enforced outside the model rather than inside its prompt: authority enumeration, spend caps, pre-send simulation, circuit breakers, account isolation, protected routing, audit logging. Use when an agent holds transaction authority. |
| `auth-implementation-patterns` | Provides authentication and authorization implementation patterns (JWT, OAuth2/OIDC, sessions, RBAC) for designing, implementing, or reviewing secure access control in applications and APIs. |
| `deps-audit` | Produces a local, best-effort dependency audit summary and remediation plan for repos with dependency manifests. |
| `gdpr-data-handling` | Implements practical GDPR-compliant data handling (privacy by design, lawful basis, DSARs, retention, vendor/transfer controls, breach readiness). Use when building or reviewing systems that process EU personal data. |
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
| `changelog-automation` | Automates changelog and release note generation from commits or PR metadata using Keep a Changelog and semantic versioning. Use when designing release workflows or standardizing commit conventions. |
| `cli-tools` | Build fast, user-friendly CLI tools with stable command surfaces, predictable output contracts (stdout vs stderr), and cross-platform behavior. Covers subcommands/flags, config precedence, interactive prompts, progress indicators, and shell completions. Use when designing or implementing CLI tools. |
| `code-review` | Provides high-signal, fast code review with selectable modes (quality, security, performance, tooling), triage of a third-party review bot's comments, an optional blind second-opinion pass, and stop conditions when the review applies its own fixes. Includes a safe-by-default script to scan diffs and produce a deterministic report. |
| `codify-exploration` | Promotes a repeated exploratory task into a deterministic, replayable on-disk unit: a written contract, a script with a pure parser, a frozen copy of its dependency, a dated fixture captured from the real source, and a test pinned to that fixture. Use when an exploration just succeeded and will be asked for again. |
| `daemon-lifecycle` | Adds a safe, supervisor-free singleton background daemon to a CLI tool: atomic state-file writes, an exclusive spawn lock with stale-holder reclaim, identity-verified process signaling, health-gated attach-vs-spawn decisions, and idle self-shutdown. Use when a CLI needs a persistent background process with no systemd, launchd, or container orchestrator supervising it, or when an existing one spawns duplicates, leaks processes, or has killed the wrong one. |
| `delivery-pipeline` | Sizes how much process one unit of work deserves using three independent signals, then runs only the phases that size earns, stopping for human approval before code is written and before commit. Use for one sequential change carried from request to commit: a new capability, a behavior change, a defect fix, a refactor, or an MVP bootstrapped from a spec. |
| `devex-review` | Reviews a proposed developer-facing product (API, CLI, SDK, library, platform, or its docs) for developer experience before it ships, distinct from reviewing its architecture or correctness. Investigates the target developer and their actual onboarding path for evidence before scoring, then rates DX per dimension on a calibrated 0-10 scale plus a separate time-to-first-result scale whose worst tier blocks rather than merely scoring low. Use on plans, design docs, or shipped products with a developer-facing surface. |
| `git-workflow` | Provides safe Git workflows for teams: clean PRs, rebasing/merging, conflict resolution, cherry-picks, safe force-push, bisect, worktrees, and recovery via reflog. Includes playbooks + safe scripts for diagnosing and fixing common Git problems. |
| `interruption-budget` | Governs when an agent interrupts a human and how it decides the rest alone: classify every question as a one-way or two-way door where it is declared, never shrink an option set to fit a tool's cap, and shape each question to be answered fast and audited later. Use when about to ask a human, when options exceed a tool's cap, or when designing a workflow that asks repeatedly. |
| `jira-issue-management` | Create, read, transition, and link Jira issues (Epics, Tasks, Bugs) through an Atlassian MCP server, driven by a project-local Jira map file that caches cloud ID, status and transition IDs, account IDs, standing Epics, and conventions. Use when work involves creating or updating Jira tickets, turning a plan into Epics and Tasks, or bootstrapping the project's Jira map. |
| `refactor-clean` | Provides an incremental, test-first refactoring workflow for reducing complexity or duplication while keeping behavior stable, best used during technical-debt cleanup or design improvement. |
| `root-cause-debugging` | Runs an evidence-first loop on a defect whose cause is unknown: journal every debug artifact before creating it, hold competing hypotheses on orthogonal axes, decide them on captured runtime values, confirm a cause only when toggling it toggles the bug, lock the fix with a failing-first test, then revert every artifact. Use when a program misbehaves and the failure does not name its own cause. |
| `shell-scripting` | Write safe, portable shell scripts (POSIX sh or Bash) for automation, CI helpers, and command-line glue: shell selection, strict-mode setup with known caveats, quoting and cleanup patterns, and shellcheck-based verification. Use for scripting, tooling, and DevOps glue code. |
| `tech-debt` | Identify, quantify, and prioritize technical debt, then turn it into an executable remediation plan with risk tiers and verification steps. Use for debt audits, cleanup planning, or when velocity and quality are degrading. |
| `testing` | Create unit tests, API contract tests, and automation strategies for existing codebases with clear decision points, pitfalls, and deterministic reporting via local scripts. |
| `tracks-conductor-protocol` | Runs a unified protocol for intake, task briefs, tracks (spec/plan), and execution with deterministic indexing, promotion (intake -> task -> track), and validation scripts. For structured work management aligned to SDD/CDD. |
