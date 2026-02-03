# Content Table

Total skills: 65

## Ai

| Skill | Summary |
| --- | --- |
| `cdd-context` | Create and maintain project context artifacts (CDD) as living documentation under docs/context/. Includes scripts to scaffold minimal context files, validate required sections, and maintain a deterministic context index. Works standalone; if other skills are available, use them for implementation details. |
| `dispatching-parallel-agents` | Split work across multiple agents in parallel when tasks are independent (no shared state, minimal file overlap). Provides a deterministic workflow to partition scope, write focused sub-agent prompts, and merge results safely. |
| `mcp-server-development` | Build high-quality MCP (Model Context Protocol) servers: workflow-first tool design, tight schemas, predictable outputs, safe error handling, and eval-driven iteration. Framework-agnostic (Node/TS or Python). No web fetching required. |
| `prompt-engineering` | Design, test, and ship production prompts fast (patterns + applied workflows). Includes prompt-as-code conventions, reusable templates, evaluation guidance, and scripts/assets for prompt iteration. Always outputs copy-pastable full prompt text. Use PROACTIVELY when building AI features, improving agent performance, or standardizing system prompts. |
| `stitch-design-md` | (Stitch) Analyze Stitch projects and synthesize a semantic design system into DESIGN.md files. Can operate without the Stitch MCP server if you provide the HTML and screenshots manually. |
| `stitch-enhance-prompt` | (Stitch) Transform vague UI ideas into polished prompts optimized for Stitch-like generators. Enhances specificity, adds UI/UX keywords, injects DESIGN.md context when present, and structures output. Does not require the Stitch MCP server. |
| `subagent-driven-development` | Use when executing an implementation plan by delegating independent tasks to fresh subagents (implementer + reviewers) with deterministic task packets and verification gates. Works with non-interactive subagents (Codex exec) and interactive environments. |

## Architecture

| Skill | Summary |
| --- | --- |
| `adr-madr-system` | Create, review, and maintain Architecture Decision Records (MADR) as individual files plus an ADR index. Optimized for spec-driven development and multi-agent workflows: enforces decision drivers, considered options, consequences, and \"supersedes\" semantics instead of editing accepted ADRs. Works standalone; if other skills exist, use them for domain/tech guidance, but keep ADRs as the decision source of truth. |
| `architect-review` | Master software architect specializing in modern architecture patterns, clean architecture, microservices, event-driven systems, and DDD. Reviews system designs and code changes for architectural integrity, scalability, and maintainability. Use PROACTIVELY for architectural decisions. |
| `backend-architect` | Expert backend architect for designing operable services and APIs: service boundaries, contracts, reliability, integration patterns, and rollout safety. Produces crisp architecture decisions and verification steps. Use PROACTIVELY when creating or changing backend services/APIs. |
| `monorepo-engineering` | Design and operate monorepos with clear boundaries, fast builds, and low-conflict collaboration. Covers workspace layout, dependency constraints, build caching, affected detection, versioning/publishing, and CI integration. Works standalone; choose tooling pragmatically (pnpm/yarn/npm, Nx/Turbo/Bazel). |

## Database

| Skill | Summary |
| --- | --- |
| `database-architect` | Design data layers and database architectures: data modeling, technology selection, schema/index strategy, lifecycle/retention, and safe evolution. Produces tradeoffs + migration/rollback plans. Use PROACTIVELY for data-model decisions. |
| `database-cost-optimization` | Reduce database-related infrastructure spend safely (instances, storage, replicas, IO) without breaking reliability or performance. Focuses on DB cost drivers, rightsizing, retention/tiering, and cost/perf tradeoffs. Works standalone. |
| `database-migration-orm` | Plan and execute ORM-managed database migrations (Prisma/TypeORM/Sequelize/EF) with zero-downtime patterns, safe backfills, and rollback discipline. Use only for ORM migration tooling (not raw SQL-file migration workflows). |
| `database-migration-sql` | Write and operate raw SQL migration files safely (forward-only / versioned SQL) with zero-downtime patterns, validation, and rollback plans. Use for .sql migration workflows (not ORM migrations). |
| `database-performance` | Diagnose and fix database performance issues (query plans, indexing, locks, connection pools, caching, partitioning). Use when latency/throughput problems point to the DB or DB access patterns. Not for schema design from scratch. |
| `postgresql-engineering` | PostgreSQL-specific schema and data-layer engineering: DDL, data types, constraints, indexing, JSONB, partitioning, RLS, and safe schema evolution. Use when you are targeting Postgres specifically. |
| `sql-querying` | Write correct, maintainable SQL and design queries (joins, CTEs, window functions) for OLTP/analytics. Use for query authoring and query-level reasoning; for DB-wide performance diagnosis use database-performance, and for schema architecture use database-architect / postgresql-engineering. |

## Devops

| Skill | Summary |
| --- | --- |
| `cloud-architect` | Design cloud platform architecture (AWS/Azure/GCP): landing zones/accounts, networking, identity/IAM boundaries, service selection, reliability/DR, and multi-region strategy. Produces architecture diagrams + risk/rollback plans. Does not own CI/CD or deep FinOps tactics. |
| `cost-optimization` | Cloud FinOps and cost governance: tagging/chargeback, budgets/anomaly detection, rightsizing, commitment strategy (RIs/Savings Plans/CUDs), and unit-cost analysis. Produces a prioritized savings plan with verification gates. Not for cloud architecture or CI/CD. |
| `deployment-engineer` | Design and implement CI/CD and deployment automation: pipeline stages, quality gates, config validation, progressive delivery, rollback/runbooks, and GitOps patterns. Use for release workflows and deployment safety. Not for cloud platform architecture or deep IaC modules. |
| `devops-engineer` | Day-2 operations and platform engineering: Docker/containerization, Kubernetes runtime patterns, environment hygiene, operational readiness, and incident response. Use when improving ops reliability or running infrastructure. For CI/CD pipeline design and rollout automation, prefer deployment-engineer. |
| `terraform-engineer` | Use when implementing infrastructure as code with Terraform across AWS, Azure, or GCP. Invoke for module development, state management, provider configuration, multi-environment workflows, infrastructure testing. |

## Docs

| Skill | Summary |
| --- | --- |
| `api-documenter` | Master API documentation with OpenAPI 3.1, AI-powered tools, and modern developer experience practices. Create interactive docs, generate SDKs, and build comprehensive developer portals. Use PROACTIVELY for API documentation or developer portal creation. |
| `code-explain` | Explain complex code clearly for humans and agents. Produce a structured walkthrough (high-level intent -> data/control flow -> key invariants -> edge cases) with optional Mermaid diagrams and actionable next steps. Use for onboarding, debugging understanding, and “how it works” docs. |
| `doc-generate` | Generate and maintain high-signal documentation from an existing codebase fast (API docs, architecture, runbooks, onboarding, reverse-specs). Includes repo scan + deterministic docs index scripts, and a spec-mining mode to reverse-engineer requirements from code. Works standalone; optionally link docs to ADRs and work artifacts for traceability. |
| `mermaid-expert` | Create Mermaid diagrams for flowcharts, sequences, ERDs, and architectures. Masters syntax for all diagram types and styling. Use PROACTIVELY for visual documentation, system diagrams, or process flows. |
| `office-files` | Work with Microsoft Office OOXML files (.docx/.pptx/.xlsx): inspect structure, extract text/tables, produce diffs, and generate clean Markdown summaries. Tool-agnostic and safe-by-default (prefers read-only workflows). Use when a task involves Word, PowerPoint, or Excel files. |
| `pdf-files` | Work with PDFs safely and repeatably: extract text/tables, convert pages to images, inspect/fill forms, and produce verifiable outputs (markdown/json/images/filled pdf). Use when a task involves PDF documents. |
| `tutorial-engineer` | Creates step-by-step tutorials and educational content from code. Transforms complex concepts into progressive learning experiences with hands-on examples. Use PROACTIVELY for onboarding guides, feature tutorials, or concept explanations. |

## Frontend

| Skill | Summary |
| --- | --- |
| `angular` | Build Angular apps with modern standalone APIs, signals, RxJS, routing, and testing. Focuses on clean component boundaries, predictable state flow, accessibility, and performance. Use for Angular implementation and refactors. |
| `frontend-design` | Implement distinctive, production-grade frontend UI (code) with high design quality. Use when you are asked to build or style components/pages/apps and you must output working UI code. For design briefs/specs/reviews (no code), use ui-design instead. |
| `nextjs` | Build React + Next.js (App Router) frontends: server/client boundaries, data fetching and caching, routing, forms/actions, accessibility, and performance. Not for generic React SPA or React Native. |
| `react` | Build React frontends (SPA/library) with modern hooks, state management, accessibility, and performance. Framework-agnostic: not Next.js-specific and not React Native. Use when implementing React components, client-side routing, data fetching/state, and React testing. |
| `react-native` | Build cross-platform mobile apps with React Native/Expo: navigation, platform handling (iOS/Android), performance (FlatList), storage, and native module integration. Not for React web or Next.js. |
| `svelte` | Build Svelte 5 and SvelteKit apps fast: runes/reactivity, component patterns, SvelteKit routing/data flow, forms/actions, SSR boundaries, and production hygiene. Includes optional guidance for TanStack Query and common component libraries. |
| `tailwind` | Build and maintain Tailwind CSS systems fast without framework lock-in: tokens (CSS variables), theme + dark mode, content globs/safelist, component variant patterns, accessibility/responsive conventions, and migration hygiene. |
| `ui-design` | One canonical, framework-agnostic UI/UX design skill: turn requirements into clear UI briefs, flows, component specs, and design-system rules; review UI code against local guidelines; prioritize accessibility, consistency, and developer-hand-off clarity. Not a Google Stitch skill. |
| `ui-visual-validator` | Verify UI changes via rigorous, evidence-based visual validation (screenshots/video/URLs). Catch regressions, design-system drift, responsive breakage, and visual accessibility issues (focus visibility, contrast, readability). Use PROACTIVELY as a final quality gate before merge. |

## Language

| Skill | Summary |
| --- | --- |
| `dotnet-core` | Build modern .NET (ASP.NET Core / .NET 8+) services: Minimal APIs, auth, DI, configuration, background jobs, and production readiness. Includes EF Core patterns and clean architecture/CQRS as optional variants. Use when implementing or reviewing .NET backend code. |
| `golang` | Build and review production Go (1.21+) services/CLIs with Go-idiomatic design, correctness, and concurrency. Includes a concurrency playbook and best-practices references (Effective Go, Code Review Comments, context/cancellation). |
| `javascript` | Master modern JavaScript with ES6+, async patterns, and Node.js APIs. Handles promises, event loops, and browser/Node compatibility. Use PROACTIVELY for JavaScript optimization, async debugging, or complex JS patterns. |
| `nestjs` | Build and evolve NestJS backends fast with correct DI/module boundaries, request lifecycle hygiene (pipes/guards/interceptors/filters), validation + serialization, OpenAPI, and testing. Optimized for spec-driven work: deterministic steps, clear output contracts, and verification gates. |
| `nodejs` | Build production-ready Node.js backend services with Express/Fastify, implementing middleware patterns, error handling, authentication, database integration, and API design best practices. Use when creating Node.js servers, REST APIs, GraphQL backends, or microservices architectures. |
| `typescript` | TypeScript best-practices + advanced typing in one skill. Use for strictness/tsconfig decisions, type-level design (generics/conditional/mapped types), fixing type errors, improving type-system performance, and building durable runtime-validated contracts at boundaries. |

## Observability

| Skill | Summary |
| --- | --- |
| `chaos-engineer` | Design and run safe chaos experiments (failure injection + game days) to validate resilience and reduce blast radius. Produces hypotheses, steady-state signals, rollback gates, and experiment specs. Use when resilience is uncertain or before high-risk changes. |
| `grafana-dashboards` | Create and manage production Grafana dashboards for real-time visualization of system and application metrics. Use when building monitoring dashboards, visualizing metrics, or creating operational observability interfaces. |
| `migration-observability` | Make database migrations safe and observable. Define progress + safety metrics, dashboards, and runbook gates (go/no-go criteria) for live migrations, backfills, and cutovers. Works standalone and is database/tooling agnostic. |
| `monitoring-expert` | End-to-end observability (logs/metrics/traces/alerts) and performance signals (profiling/load tests/capacity planning). Use when instrumenting services, setting alert strategy, or building an observability stack. For Grafana dashboard implementation/JSON, prefer grafana-dashboards if available. |
| `performance` | End-to-end performance optimization skill combining orchestration (workflow) and deep-dive engineering. Establishes baselines, profiles bottlenecks, proposes fixes with measurable impact, and adds regression guardrails. Includes a safe-by-default perf wrapper script to capture repo signals and write a deterministic report. Use PROACTIVELY for latency/throughput/resource issues, scalability work, or perf gating. |
| `sre-engineer` | Site Reliability Engineering for production systems: define SLIs/SLOs and error budgets, design alerting and runbooks, reduce toil with automation, and improve incident response. Use when you need reliability targets and operational practices (not just dashboards). |

## Security

| Skill | Summary |
| --- | --- |
| `auth-implementation-patterns` | Master authentication and authorization patterns including JWT, OAuth2, session management, and RBAC to build secure, scalable access control systems. Use when implementing auth systems, securing APIs, or debugging security issues. |
| `deps-audit` | Audit dependencies fast for vulnerabilities, licenses, and supply-chain risk across common ecosystems (Node/Python/Go/Rust/etc). Produces a short risk summary plus an executable remediation plan (compatible with tracks-conductor-protocol). Includes scripts to detect manifests and generate a deterministic audit report under docs/_docgen. Use PROACTIVELY for security posture checks, dependency upgrades, or pre-release hardening. |
| `gdpr-data-handling` | Implement practical GDPR-compliant data handling (privacy by design, lawful basis, DSARs, retention, vendor/transfer controls, breach readiness). Use when building or reviewing systems that process EU personal data. |
| `secrets-management` | Secure secrets handling for CI/CD and runtime: secret inventory, access boundaries, short-lived identity (OIDC/workload identity), rotation, auditing, and leak response. Works across Vault and cloud-native secret managers. |
| `security-auditor` | Expert security auditor specializing in DevSecOps, comprehensive cybersecurity, and compliance frameworks. Masters vulnerability assessment, threat modeling, secure authentication (OAuth2/OIDC), OWASP standards, cloud security, and security automation. Handles DevSecOps integration, compliance (GDPR/HIPAA/SOC2), and incident response. Use PROACTIVELY for security audits, DevSecOps, or compliance implementation. |

## Workflow

| Skill | Summary |
| --- | --- |
| `brainstorming` | Clarify ambiguous work through structured brainstorming: ask focused questions, propose 2-3 approaches with tradeoffs, and produce a concise design brief (goals, non-goals, constraints, risks, validation). Use when requirements are unclear or before large/irreversible changes. |
| `changelog-automation` | Automate changelog generation from commits, PRs, and releases following Keep a Changelog format. Use when setting up release workflows, generating release notes, or standardizing commit conventions. |
| `cli-tools` | Build fast, user-friendly CLI tools with stable command surfaces, predictable output contracts (stdout vs stderr), and cross-platform behavior. Covers subcommands/flags, config precedence, interactive prompts, progress indicators, and shell completions. Use when designing or implementing CLI tools. |
| `code-review` | High-signal, fast code review with selectable modes (quality/tone, security/performance, tooling/automation). Includes a safe-by-default review script to summarize diffs, scan for risky patterns, and produce a deterministic report. Works standalone; if other skills are available, use them for domain/tech-specific checks. |
| `git-workflow` | Master Git workflows for teams: clean PRs, rebasing/merging, conflict resolution, cherry-picks, safe force-push, bisect, worktrees, and recovery via reflog. Includes playbooks + safe scripts for diagnosing and fixing common Git problems. |
| `refactor-clean` | Refactor code safely and quickly using clean-code + SOLID principles with an incremental, test-first workflow. Includes a lightweight hotspot scan script to find high-impact refactor targets. Use PROACTIVELY for refactoring tangled code, reducing duplication/complexity, and preparing modules for new features without behavior regressions. |
| `tech-debt` | Identify, quantify, and prioritize technical debt fast, then turn it into an executable remediation plan (SDD/CDD friendly). Produces a debt register with ROI estimates, risk tiers, and a track/task breakdown compatible with tracks-conductor-protocol and adr-madr-system. Use PROACTIVELY for debt audits, cleanup planning, or when velocity/quality is degrading. |
| `testing` | Unified testing skill for speed + quality. Supports two modes: unit test generation and end-to-end/automation strategy. Includes safe-by-default scripts to scaffold test plans and generate a deterministic testing report. Works standalone; if stack-specific testing skills exist, prefer them for framework/tooling details. |
| `tracks-conductor-protocol` | Unified protocol + tooling for spec-driven and context-driven development across intake, task briefs, tracks (spec/plan), and execution. Designed for multi-agent workflows with deterministic indexing, promotion (intake -> task -> track), and validation scripts. Works standalone; if tech/framework skills are available, use them for implementation details. |
