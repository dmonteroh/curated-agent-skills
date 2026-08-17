---
name: git-workflow
description: "Master Git workflows for teams: clean PRs, rebasing/merging, conflict resolution, cherry-picks, safe force-push, bisect, worktrees, and recovery via reflog. Includes playbooks + safe scripts for diagnosing and fixing common Git problems."
metadata:
  category: workflow
---
# git-workflow

Provides safe, fast Git workflows for multi-contributor repos.

This skill is intentionally practical: it optimizes for **clean history**, **low-conflict collaboration**, and **recoverability** when something goes wrong.

## Required inputs

- Target repo path (or confirm current working directory is a Git repo).
- Branch goal (clean PR, rebase/merge, cherry-pick/backport, recovery, bisect, worktrees).
- Base branch name (default: `main`) and remote name (default: `origin`).
- Risk tolerance for history edits (allowed to rebase/squash? force-with-lease ok?).

## Prerequisites

- `git` CLI is available in the environment.
- Network access is optional. If offline or no remotes are configured, skip steps that require `git fetch` or `git push`.

## Use this skill when

- Preparing a clean PR (commit messages, splitting/squashing, rebase onto main).
- Resolving merge conflicts or untangling diverged branches.
- Applying specific commits across branches (cherry-pick, backports).
- Recovering lost work (reflog, reset, restore).
- Running archaeology (bisect) to find a regression.
- Working on multiple branches in parallel (worktrees).
- Merging a PR via `gh pr merge` and confirming the merge actually landed.

## Do not use this skill when

- No Git repository is available.
- The request is purely about product/code design (no Git workflow concerns).

## Safety defaults (non-negotiable)

- Prefer `git push --force-with-lease` over `--force`.
- Before history surgery (rebase/reset): create a backup ref:
  - `git branch backup/<name>-$(date +%Y%m%d-%H%M%S)`
- Never rewrite shared history unless the branch is controlled or explicit agreement exists.

## Step-by-step workflow

1. **Identify repo state (read-only).**
   - Run `git status -sb`, `git branch -vv`, `git remote -v`.
   - Output: current branch, upstream, ahead/behind, working tree state.
2. **Pick the workflow path.**
   - If clean PR needed → follow `references/finish-branch.md` and `references/commit-messages.md`.
   - If conflicts or diverged branches → follow `references/rebase-and-conflicts.md`.
   - If applying specific commits → use `git cherry-pick` flow in `references/quick-cheatsheet.md`.
   - If recovery/undo → follow `references/recovery.md`.
   - If regression hunting → follow `references/bisect.md`.
   - If parallel branches → follow `references/worktrees.md`.
   - Output: chosen path + reason.
3. **Create safety backup (when history changes).**
   - If doing rebase/reset/force push, create a backup ref first.
   - Output: backup branch name.
4. **Execute the chosen playbook.**
   - Follow the playbook steps and record each Git command.
   - Output: command log and any conflicts resolved.
5. **Verify and summarize.**
   - Run `git status -sb` and `git log --oneline -n 10`.
   - Output: final status, branch head, and next steps (push/PR).

## Decision points

- **Rebase vs merge?** If clean linear history is required and the branch is locally owned, rebase. Otherwise, merge.
- **Force push allowed?** Only use `--force-with-lease` on branches with explicit ownership.
- **Conflicts too risky?** If conflicts touch high-risk files, stop and request guidance before continuing.

## Common pitfalls

- Rebasing a shared branch without agreement.
- Using `git push --force` instead of `--force-with-lease`.
- Losing uncommitted changes before a reset (stash or commit first).
- Forgetting to set or verify the upstream branch before pushing.
- Retrying `gh pr merge` after it exits non-zero. The merge can already have succeeded server-side before the client-visible failure (cited: `cli/cli#3442`, `cli/cli#13380`) — a blind retry can then error confusingly against an already-merged PR. On any non-zero exit, stop and query authoritative PR state instead of retrying, e.g. `gh pr view <number> --json state,mergedAt,mergeCommit,mergeStateStatus`, and decide the next step from that, never from the exit code alone.
- Proving a PR merged with `git merge-base --is-ancestor <head_sha> origin/<base>`. GitHub's squash and rebase merges deliberately create a *new* commit on the base branch, so the original PR head SHA is never an ancestor of it even when the PR merged cleanly — this check gives a false negative on exactly the two merge strategies most teams use. Confirm merge state from `gh pr view`/`gh api` output instead, never from an ancestor check.

## Scripts

Scripts are optional helpers and use only local `git` commands.

- `scripts/git_doctor.sh`
  - Usage: `./scripts/git_doctor.sh`
  - Verifies: prints repo, branch, status, remotes, and recent history.
- `scripts/git_prune_local_branches.sh`
  - Usage: `./scripts/git_prune_local_branches.sh [base]`
  - Verifies: lists deleted local branches and prints `OK`.
  - Notes: attempts `git fetch --prune`; if offline, the script safely continues.

## Examples

**Example: clean PR with rebase**

Input: “Clean up my branch before PR; base is main.”

Output:
- Chosen path: clean PR
- Commands:
  - `git fetch origin`
  - `git branch backup/feature-clean-20240101-120000`
  - `git rebase origin/main`
  - `git log --oneline -n 5`
- Result: branch is up to date with `origin/main`, no conflicts

**Example: recover a lost commit**

Input: “I reset too far; find the lost commit.”

Output:
- Chosen path: recovery
- Commands:
  - `git reflog -n 20`
  - `git branch backup/recover-20240101-120000`
  - `git reset --hard <sha>`
- Result: HEAD restored to the selected commit

## Output contract

When this skill runs, report in this format:

- **Repo state:** current branch, upstream, ahead/behind, dirty/clean.
- **Chosen path:** which playbook and why.
- **Commands executed:** ordered list.
- **Risk notes:** any history rewrites or force pushes.
- **Verification:** final `git status -sb` + `git log --oneline -n 5`.
- **Next steps:** push/PR guidance or follow-up questions.

## Quickstart

```sh
./scripts/git_doctor.sh
./scripts/git_prune_local_branches.sh
```

## Core playbooks (load as needed)

- Start with `references/README.md` for the index and summaries.
- External references are optional; use only if network access is permitted.
