# Content Table

Total skills: 66

## Ai

| Skill | Summary |
| --- | --- |
| `cdd-context` | Create and maintain CDD project context docs (product, tech stack, workflow) when setting up or updating docs/context, with optional scaffolding, indexing, validation, and a brief snapshot. |
| `google-stitch-ai` | Create DESIGN.md summaries from Google Stitch projects or offline assets for UI design workflows, and refine Stitch-ready UI prompts using extracted design tokens. |
| `mcp-server-development` | Build high-quality MCP (Model Context Protocol) servers: workflow-first tool design, tight schemas, predictable outputs, safe error handling, and eval-driven iteration. Framework-agnostic (Node/TS or Python). No web fetching required. |
| `prompt-engineering` | Designs, tests, and ships production prompts using prompt-as-code workflows, templates, evaluation guidance, and optional scripts/assets. Returns a full copy/paste prompt block. Use when building AI features, improving agent performance, or standardizing system prompts. |
| `subagent-orchestrator` | Decide whether and how to split work across subagents, then orchestrate execution safely with mode selection, claim-set control, barriered verification, and deterministic integration. |

## Architecture

| Skill | Summary |
| --- | --- |
| `adr-madr-system` | Create, review, and maintain Architecture Decision Records (MADR) as individual files plus an ADR index when documenting or superseding architectural decisions. Focuses on decision drivers, options, consequences, and supersedes semantics so accepted ADRs remain immutable. |
| `architect-review` | Review system designs and major changes for architectural integrity, scalability, and maintainability; use for architecture decisions, tradeoffs, and risks across distributed systems and clean architecture patterns. |
| `backend-architect` | Guides backend architecture for operable services and APIs, covering boundaries, contracts, reliability, integration patterns, and rollout safety. Use when designing or changing backend services/APIs and their operability plans. |
| `monorepo-engineering` | Design and operate monorepos with clear boundaries, fast builds, and low-conflict collaboration. Covers workspace layout, dependency constraints, build caching, affected detection, versioning/publishing, and CI integration. Works standalone; choose tooling pragmatically (pnpm/yarn/npm, Nx/Turbo/Bazel). |

## Database

| Skill | Summary |
| --- | --- |
| `database-architect` | Design data layers and database architectures by selecting storage models, modeling schemas, and planning safe evolution with tradeoffs and migration/rollback plans. Use when making data-layer decisions or re-architecting storage. |
| `database-cost-optimization` | Reduce database infrastructure spend when costs need optimization by analyzing cost drivers, right-sizing compute/storage/replicas, and proposing verified rollback-ready changes without compromising reliability. |
| `database-migration-orm` | Plan and execute ORM-managed database migrations (Prisma/TypeORM/Sequelize/EF) with zero-downtime patterns, safe backfills, and rollback discipline. Use only for ORM migration tooling (not raw SQL-file migration workflows). |
| `database-migration-sql` | Plan and write forward-only SQL migration files with zero-downtime patterns, validation, rollback guidance, and production safety checks for PostgreSQL, MySQL, and SQL Server. |
| `database-performance` | Diagnose and fix database performance issues (slow queries, locks, pool saturation, caching, partitioning) using evidence from metrics and query plans. |
| `postgresql-engineering` | PostgreSQL-specific schema and data-layer engineering: DDL, data types, constraints, indexing, JSONB, partitioning, RLS, and safe schema evolution. Use when targeting Postgres specifically. |
| `sql-querying` | Write correct, maintainable SQL queries (joins, CTEs, window functions) and reason about their results for OLTP or analytics tasks. |

## Design

| Skill | Summary |
| --- | --- |
| `frontend-design` | Implement distinctive, production-grade frontend UI code with high design quality. Use when asked to build or style components/pages/apps and deliver working UI code; avoid for design-only briefs without implementation. |
| `ui-design` | One canonical, framework-agnostic UI/UX design skill: turn requirements into clear UI briefs, flows, component specs, and design-system rules; review UI code against local guidelines; prioritize accessibility, consistency, and developer-hand-off clarity. Not a Google Stitch skill. |
| `ui-visual-validator` | Verifies UI changes via rigorous, evidence-based visual validation (screenshots/video/URLs) to catch regressions, design-system drift, responsive breakage, and visual accessibility issues. |

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
| `mermaid-expert` | Create Mermaid diagrams for flowcharts, sequences, ERDs, and architecture visuals with clear syntax, styling, and delivery guidance. |
| `office-files` | Work with Microsoft Office OOXML files (.docx/.pptx/.xlsx): inspect structure, extract text/tables, produce diffs, and generate clean Markdown summaries. Tool-agnostic and safe-by-default (prefers read-only workflows). Use when a task involves Word, PowerPoint, or Excel files. |
| `pdf-files` | Work with PDFs safely and repeatably: extract text/tables, convert pages to images, inspect/fill forms, and produce verifiable outputs (markdown/json/images/filled pdf). Use when a task involves PDF documents. |
| `tutorial-engineer` | Creates step-by-step technical tutorials and onboarding guides from code or system requirements when teams need progressive, hands-on learning paths for developers. |

## Frontend

| Skill | Summary |
| --- | --- |
| `angular` | Guides Angular implementation and refactors using standalone APIs, signals, RxJS, routing, and testing. Focuses on clean component boundaries, predictable state flow, accessibility, and performance. Use when work is Angular-specific. |
| `nextjs` | Build React + Next.js (App Router) frontends: server/client boundaries, data fetching and caching, routing, forms/actions, accessibility, and performance. Not for generic React SPA or React Native. |
| `react` | Build React frontends (SPA/library) with modern hooks, state management, accessibility, and performance. Framework-agnostic: not Next.js-specific and not React Native. Use when implementing React components, client-side routing, data fetching/state, and React testing. |
| `react-native` | Build cross-platform mobile apps with React Native/Expo: navigation, platform handling (iOS/Android), performance (FlatList), storage, and native module integration. Not for React web or Next.js. |
| `svelte` | Build Svelte 5 and SvelteKit apps fast: runes/reactivity, component patterns, SvelteKit routing/data flow, forms/actions, SSR boundaries, and production hygiene. Includes optional guidance for TanStack Query and common component libraries. |
| `tailwind` | Build and maintain Tailwind CSS systems fast without framework lock-in: tokens (CSS variables), theme + dark mode, content globs/safelist, component variant patterns, accessibility/responsive conventions, and migration hygiene. |

## Git

| Skill | Summary |
| --- | --- |
| `smart-conventional-commits` | Create conventional commits from user intent and git diff context, including auto-staging, branch-aware type inference, and concise mandatory title/body generation. Use when users ask to commit changes or draft commit messages. |

## Language

| Skill | Summary |
| --- | --- |
| `dotnet-core` | Build and review modern .NET (ASP.NET Core / .NET 8+) backend services with DI, auth, data access, and production readiness. Use for implementing or auditing .NET server code and architecture choices. |
| `golang` | Build and review production Go (1.21+) services/CLIs with idiomatic design, correctness, and safe concurrency/cancellation patterns. |
| `javascript` | Build and debug modern JavaScript (ES6+) with async patterns and Node.js/browser compatibility when authoring, modernizing, or diagnosing JS. |
| `nestjs` | Build and evolve NestJS backends with correct DI/module boundaries, request lifecycle hygiene (pipes/guards/interceptors/filters), validation + serialization, OpenAPI, and testing. Use when adding or refactoring NestJS endpoints/modules and needing deterministic steps, output contracts, and verification gates. |
| `nodejs` | Use when building production-ready Node.js backend services with Express or Fastify, covering API design, middleware, authentication, error handling, and database integration. |
| `python` | Build modern Python 3.x services and libraries with async patterns, robust typing, and production-ready practices. Use for Python implementation, refactors, and tooling guidance when a Python runtime is required. |
| `typescript` | Provides TypeScript architecture and typing guidance for strictness/tsconfig decisions, advanced type design, fixing type errors, type-checking performance, and boundary runtime validation; use when resolving TypeScript typing or configuration issues. |

## Observability

| Skill | Summary |
| --- | --- |
| `chaos-engineer` | Design and run safe chaos experiments (failure injection + game days) to validate resilience and reduce blast radius. Produces hypotheses, steady-state signals, rollback gates, and experiment specs. Use when resilience is uncertain or before high-risk changes. |
| `grafana-dashboards` | Provides guidance to create and manage production Grafana dashboards for real-time visualization of system and application metrics. Use when building monitoring dashboards, visualizing metrics, or creating operational observability interfaces. |
| `migration-observability` | Make database migrations safe and observable. Define progress + safety metrics, dashboards, and runbook gates (go/no-go criteria) for live migrations, backfills, and cutovers. Works standalone and is database/tooling agnostic. |
| `monitoring-expert` | Provides end-to-end observability across logs, metrics, traces, alerting, and performance testing. Use when instrumenting services, setting alert strategy, or designing an observability stack. |
| `performance` | End-to-end performance optimization workflow for baselining, profiling bottlenecks, proposing measurable fixes, and adding regression guardrails. Includes a safe-by-default scan/report script to capture repo signals and write a deterministic report. Use for latency/throughput/resource issues, scalability work, or performance gating. |
| `sre-engineer` | Site Reliability Engineering for production systems: define SLIs/SLOs and error budgets, design alerting and runbooks, reduce toil with automation, and improve incident response. Use when you need reliability targets and operational practices (not just dashboards). |

## Security

| Skill | Summary |
| --- | --- |
| `auth-implementation-patterns` | Provides authentication and authorization implementation patterns (JWT, OAuth2/OIDC, sessions, RBAC) for designing, implementing, or reviewing secure access control in applications and APIs. |
| `deps-audit` | Produces a local, best-effort dependency audit summary and remediation plan for repos with dependency manifests. |
| `gdpr-data-handling` | Implement practical GDPR-compliant data handling (privacy by design, lawful basis, DSARs, retention, vendor/transfer controls, breach readiness). Use when building or reviewing systems that process EU personal data. |
| `secrets-management` | Secure secrets handling for CI/CD and runtime: secret inventory, access boundaries, short-lived identity (OIDC/workload identity), rotation, auditing, and leak response. Works across Vault and cloud-native secret managers. |
| `security-auditor` | Provides a structured security audit workflow for DevSecOps, application security, and compliance readiness, used for scoped assessments, threat modeling, testing, and remediation planning. |

## Workflow

| Skill | Summary |
| --- | --- |
| `brainstorming` | Clarify ambiguous work through structured brainstorming: ask focused questions, propose 2-3 approaches with tradeoffs, and produce a concise design brief (goals, non-goals, constraints, risks, validation). Use when requirements are unclear or before large/irreversible changes. |
| `changelog-automation` | Automate changelog and release note generation from commits or PR metadata using Keep a Changelog and semantic versioning. Use when designing release workflows or standardizing commit conventions. |
| `cli-tools` | Build fast, user-friendly CLI tools with stable command surfaces, predictable output contracts (stdout vs stderr), and cross-platform behavior. Covers subcommands/flags, config precedence, interactive prompts, progress indicators, and shell completions. Use when designing or implementing CLI tools. |
| `code-review` | Provides high-signal, fast code review with selectable modes (quality, security, performance, tooling). Includes an optional safe-by-default review script to summarize diffs, scan for risky patterns, and produce a deterministic report. |
| `git-workflow` | Master Git workflows for teams: clean PRs, rebasing/merging, conflict resolution, cherry-picks, safe force-push, bisect, worktrees, and recovery via reflog. Includes playbooks + safe scripts for diagnosing and fixing common Git problems. |
| `refactor-clean` | Provides an incremental, test-first refactoring workflow for reducing complexity or duplication while keeping behavior stable, best used during technical-debt cleanup or design improvement. |
| `shell-scripting` | Write safe, portable shell scripts (POSIX/Bash) for automation and CI. Use for scripting, tooling, and DevOps glue code. |
| `tech-debt` | Identify, quantify, and prioritize technical debt, then turn it into an executable remediation plan with ROI estimates, risk tiers, and verification steps. Use for debt audits, cleanup planning, or when velocity and quality are degrading. |
| `testing` | Create unit tests, API contract tests, and automation strategies for existing codebases with clear decision points, pitfalls, and deterministic reporting via local scripts. |
| `tracks-conductor-protocol` | Run a unified protocol for intake, task briefs, tracks (spec/plan), and execution with deterministic indexing, promotion (intake -> task -> track), and validation scripts. Use for structured work management aligned to SDD/CDD. |
