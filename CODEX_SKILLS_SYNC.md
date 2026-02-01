# Codex Skills Sync

This repo includes a small installer/updater script for copying skills from this repo into your local Codex skills directory.

Script: `scripts/codex_skills_sync.py`

## What It Does

- Copies selected skill folders (those containing `SKILL.md`) into a destination directory (default: `~/.codex/skills`).
- Lets you select skills by name, index, or range.
- Safe-by-default:
  - does not overwrite existing installed skills unless you pass `--force`
  - does not delete anything unless you pass `--prune`
  - when overwriting with `--force`, backups are opt-in via `--backup`

## Quick Start (Interactive)

Runs interactively (prompts for install directory and which skills to install):

```sh
./scripts/codex_skills_sync.py
```

## Recommended Commands

Install the recommended OS-level bundle (workflow/protocol + indexing):

```sh
./scripts/codex_skills_sync.py --select "adr-madr-system,brainstorming,git-workflow,cdd-context,doc-generate,dispatching-parallel-agents,mermaid-expert,subagent-driven-development,tracks-conductor-protocol"
```

Install the recommended architecture bundle (system + backend + cloud; no DB-architect):

```sh
./scripts/codex_skills_sync.py --select "architect-review,backend-architect,cloud-architect,sre-engineer,code-review,code-explain,auth-implementation-patterns,tech-debt,deps-audit,refactor-clean"
```

Install the recommended database bundle (DB-agnostic architecture + migrations + performance):

```sh
./scripts/codex_skills_sync.py --select "database-architect,sql-querying,database-performance,migration-observability"
```

Install the recommended testing bundle:

```sh
./scripts/codex_skills_sync.py --select "testing,ui-visual-validator"
```

Install the recommended security bundle:

```sh
./scripts/codex_skills_sync.py --select "security-auditor,secrets-management,gdpr-data-handling,auth-implementation-patterns"
```

Install the recommended DevOps bundle (CI/CD + day-2 ops + IaC):

```sh
./scripts/codex_skills_sync.py --select "deployment-engineer,devops-engineer,terraform-engineer,monitoring-expert,grafana-dashboards,sre-engineer"
```

Install the recommended documentation/enablement bundle:

```sh
./scripts/codex_skills_sync.py --select "doc-generate,code-explain,tutorial-engineer,mermaid-expert"
```

Install the recommended observability/monitoring bundle (day-2 focused):

```sh
./scripts/codex_skills_sync.py --select "monitoring-expert,grafana-dashboards,sre-engineer,migration-observability"
```

Install the recommended design bundle (spec + implementation + visual QA):

```sh
./scripts/codex_skills_sync.py --select "ui-design,frontend-design,ui-visual-validator"
```

## Common Commands

List skills available in this repo:

```sh
./scripts/codex_skills_sync.py --list
```

Dry-run installing a subset (no filesystem writes):

```sh
./scripts/codex_skills_sync.py --select "1-10" --dry-run
```

Install specific skills by name:

```sh
./scripts/codex_skills_sync.py --select "tracks-conductor-protocol,adr-madr-system"
```

Install everything:

```sh
./scripts/codex_skills_sync.py --all
```

Install to a custom directory:

```sh
./scripts/codex_skills_sync.py --dest "~/somewhere/skills" --select "react-pro,svelte-pro"
```

Overwrite existing installed skills:

```sh
./scripts/codex_skills_sync.py --select "all" --force
```

Overwrite and keep timestamped backups (opt-in):

```sh
./scripts/codex_skills_sync.py --select "all" --force --backup
```

Prune installed skills not in your selected set (destructive):

```sh
./scripts/codex_skills_sync.py --select "all" --prune
```

List what’s currently installed in the destination:

```sh
./scripts/codex_skills_sync.py --list-installed
```

Show version:

```sh
./scripts/codex_skills_sync.py --version
```

## Selection Syntax

`--select` accepts:

- `all` or `*`
- indices: `1,4,8`
- ranges: `1-5`
- names: `react-pro,svelte-pro`
- mixed: `1-5,react-pro`

## Output

- Human-facing progress goes to stderr.
- stdout always prints a machine-friendly summary:

```text
installed=<n>
skipped=<n>
failed=<n>
pruned=<n>
```
