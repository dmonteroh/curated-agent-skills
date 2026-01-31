---
name: git-workflow
description: Master Git workflows for teams: clean PRs, rebasing/merging, conflict resolution, cherry-picks, safe force-push, bisect, worktrees, and recovery via reflog. Includes playbooks + safe scripts for diagnosing and fixing common Git problems.
---

# git-workflow

Use Git safely and fast in multi-agent, multi-contributor repos.

This skill is intentionally practical: it optimizes for **clean history**, **low-conflict collaboration**, and **recoverability** when something goes wrong.

## Use this skill when

- Preparing a clean PR (commit messages, splitting/squashing, rebase onto main).
- Resolving merge conflicts or untangling diverged branches.
- Applying specific commits across branches (cherry-pick, backports).
- Recovering lost work (reflog, reset, restore).
- Running archaeology (bisect) to find a regression.
- Working on multiple branches in parallel (worktrees).

## Do not use this skill when

- You are not operating on a Git repository.
- The request is purely about product/code design (no Git workflow concerns).

## Safety defaults (non-negotiable)

- Prefer `git push --force-with-lease` over `--force`.
- Before history surgery (rebase/reset): create a backup ref:
  - `git branch backup/<name>-$(date +%Y%m%d-%H%M%S)`
- Never rewrite shared history unless you control the branch (or have explicit agreement).

## Quickstart

```sh
./git-workflow/scripts/git_doctor.sh
./git-workflow/scripts/git_prune_local_branches.sh
```

## Core playbooks (load as needed)

- `references/quick-cheatsheet.md` (high-signal commands)
- `references/commit-messages.md` (clean, reviewable commits)
- `references/rebase-and-conflicts.md` (rebase workflows + conflict resolution)
- `references/finish-branch.md` (verification-first branch finishing / PR flow)
- `references/recovery.md` (reflog, reset, restore, undo)
- `references/bisect.md` (find the regression commit)
- `references/worktrees.md` (parallel work without stashing)
- `references/external-references.md` (curated external references)
