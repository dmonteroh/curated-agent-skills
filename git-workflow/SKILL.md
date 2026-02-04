---
name: git-workflow
description: "Master Git workflows for teams: clean PRs, rebasing/merging, conflict resolution, cherry-picks, safe force-push, bisect, worktrees, and recovery via reflog. Includes playbooks + safe scripts for diagnosing and fixing common Git problems."
category: workflow
---

# git-workflow

Use Git safely and fast in multi-contributor repos.

This skill is intentionally practical: it optimizes for **clean history**, **low-conflict collaboration**, and **recoverability** when something goes wrong.

## Required inputs

- Target repo path (or confirm current working directory is a Git repo).
- Branch goal (clean PR, rebase/merge, cherry-pick/backport, recovery, bisect, worktrees).
- Base branch name (default: `main`) and remote name (default: `origin`).
- Risk tolerance for history edits (allowed to rebase/squash? force-with-lease ok?).

## Use this skill when

- Preparing a clean PR (commit messages, splitting/squashing, rebase onto main).
- Resolving merge conflicts or untangling diverged branches.
- Applying specific commits across branches (cherry-pick, backports).
- Recovering lost work (reflog, reset, restore).
- Running archaeology (bisect) to find a regression.
- Working on multiple branches in parallel (worktrees).

## Trigger phrases

- “clean up my commits”
- “rebase onto main” / “my branch diverged”
- “cherry-pick this fix” / “backport a commit”
- “I lost commits” / “undo the last push”
- “find the commit that broke it”
- “use worktrees for parallel work”

## Do not use this skill when

- You are not operating on a Git repository.
- The request is purely about product/code design (no Git workflow concerns).

## Safety defaults (non-negotiable)

- Prefer `git push --force-with-lease` over `--force`.
- Before history surgery (rebase/reset): create a backup ref:
  - `git branch backup/<name>-$(date +%Y%m%d-%H%M%S)`
- Never rewrite shared history unless you control the branch (or have explicit agreement).

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

- **Rebase vs merge?** If clean linear history is required and you own the branch, rebase. Otherwise, merge.
- **Force push allowed?** Only use `--force-with-lease` on branches you control.
- **Conflicts too risky?** If conflicts touch high-risk files, stop and request guidance before continuing.

## Common pitfalls

- Rebasing a shared branch without agreement.
- Using `git push --force` instead of `--force-with-lease`.
- Losing uncommitted changes before a reset (stash or commit first).
- Forgetting to set or verify the upstream branch before pushing.

## Scripts

Scripts are optional helpers and use only local `git` commands.

- `scripts/git_doctor.sh`
  - Usage: `./scripts/git_doctor.sh`
  - Verifies: prints repo, branch, status, remotes, and recent history.
- `scripts/git_prune_local_branches.sh`
  - Usage: `./scripts/git_prune_local_branches.sh [base]`
  - Verifies: lists deleted local branches and prints `OK`.

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

When you run this skill, report in this format:

- **Repo state:** current branch, upstream, ahead/behind, dirty/clean.
- **Chosen path:** which playbook and why.
- **Commands executed:** ordered list.
- **Risk notes:** any history rewrites or force pushes.
- **Verification:** final `git status -sb` + `git log --oneline -n 5`.
- **Next steps:** push/PR guidance or follow-up questions.

## Trigger test

- “My branch diverged from main and I need a clean PR.”
- “I need to backport this commit to the release branch.”

## Quickstart

```sh
./scripts/git_doctor.sh
./scripts/git_prune_local_branches.sh
```

## Core playbooks (load as needed)

- Start with `references/README.md` for the index and summaries.
