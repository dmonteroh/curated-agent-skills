---
name: git-workflow
description: "Provides safe Git workflows for teams: clean PRs, rebasing/merging, conflict resolution, cherry-picks, safe force-push, bisect, worktrees, and recovery via reflog. Includes playbooks + safe scripts for diagnosing and fixing common Git problems."
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
- Answering a history question — when a line changed, who changed it, which commit introduced or removed a string — with cited evidence.
- Inspecting repository state on request without changing it.
- Working on multiple branches in parallel (worktrees).
- Merging a PR via `gh pr merge` and confirming the merge actually landed.

## Do not use this skill when

- No Git repository is available.
- The request is purely about product/code design (no Git workflow concerns).

## Safety defaults

- Prefer `git push --force-with-lease` over `--force`.
- Before history surgery (rebase/reset): create a backup ref:
  - `git branch backup/<name>-$(date +%Y%m%d-%H%M%S)`
- Never rewrite shared history unless the branch is controlled or explicit agreement exists.

## Mode gate

Classify the request into exactly one mode before running the first command. This partitions by **write authority** and is orthogonal to the playbook paths in step 2, which partition by task: settle the mode first, then choose a path inside it.

- `STATUS` — inspect branch, diff, or working-tree state. Changes nothing.
- `HISTORY` — answer when, where, who, why, or which commit changed something. Changes nothing.
- `COMMIT` — stage and commit local changes.
- `REBASE` — rebase, squash, fixup, autosquash, reorder, split, or any other history rewrite.

Do not commit, rebase, push, force-push, reset, pop a stash, or delete anything unless the request explicitly asked for that operation. A `STATUS` or `HISTORY` request ends in a report: state the findings and stop, even when the fix looks obvious and trivial — propose it and wait.

Before any write (`COMMIT` or `REBASE`), all five must hold:

1. The current branch is known.
2. Dirty work in the tree is accounted for.
3. Pushed/upstream status is known, or explicitly recorded as unknown.
4. The operation matches what was requested.
5. A recovery path is known: `git rebase --abort`, a reflog hash, or an untouched worktree.

If any of the five is unresolved, stop and resolve it before writing. An unknown here is a reason to ask, not to proceed on the more likely reading.

## Workflow

1. **Identify repo state (read-only).**
   - Run `git status -sb`, `git branch -vv`, `git remote -v`.
   - For history work or any rewrite, gather independent facts as well: `git diff --stat`, `git diff --staged --stat`, `git branch --show-current`, `git log --oneline -n 30`, `git rev-parse --abbrev-ref @{upstream}`, `git merge-base HEAD origin/main`. (`-n 30` is a chosen starting window, not a limit — widen it when the answer needs older history.)
   - Expect some of these to fail: no upstream is configured, the default branch is not `main`, the repo has no remote. Fall back to the best available branch, or record the fact as unestablished. **Never treat a failed lookup as proof** — a missing upstream is not evidence that nothing was pushed, and a `git merge-base` that errors because `origin/main` does not exist says nothing about whether the branch diverged.
   - Output: current branch, upstream, ahead/behind, working tree state, and every fact that could not be established.
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

## History questions

Choose the command from the question that was asked, not from the tool that comes to mind first:

| Question | Command |
| --- | --- |
| Did the count of an exact string change? | `git log -S "text"` |
| Did any diff touch lines matching a pattern? | `git log -G "regex"` |
| Who last changed these specific lines? | `git blame -L <start>,<end> -- <file>` |
| What is one file's history across renames? | `git log --follow -- <file>` |
| What exactly did this candidate commit do? | `git show <hash>` |
| Which commit first broke a deterministic check? | `git bisect` — only with a pass/fail command and known good/bad bounds (`references/bisect.md`) |
| What moved a local ref recently? | `git reflog` (`references/recovery.md`) |

`-S` and `-G` are easy to swap, and the difference decides the answer. `-S` counts occurrences of the string and reports only commits where that count changed, so a commit that edits the line *around* the string does not match. `-G` matches any diff line touching the pattern, including that edit. Asking "when did this call disappear" wants `-S`; asking "which commits ever touched this call site" wants `-G`.

Cite the evidence in the answer: commit hash, subject, file path, and the line or diff context that supports it. Where the evidence is ambiguous — a squashed import commit, a wholesale reformat that rewrote `blame` — say what remains unproven instead of resolving it by assertion.

## Common pitfalls

- Losing uncommitted changes before a reset (stash or commit first).
- Forgetting to set or verify the upstream branch before pushing.
- Reaching for `git rebase -i` where no interactive editor can be attached (CI job, hook, headless agent session). The interactive rebase opens a sequence editor and waits; with none available it stalls or aborts rather than rewriting anything, and the failure looks like a git problem instead of an environment one. Use the editor-free autosquash form in `references/rebase-and-conflicts.md`.
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

- **Mode:** `STATUS`, `HISTORY`, `COMMIT`, or `REBASE`, and what in the request set it.
- **Repo state:** current branch, upstream, ahead/behind, dirty/clean, plus any fact that could not be established.
- **Chosen path:** which playbook and why.
- **Commands executed:** ordered list.
- **Evidence (`HISTORY` answers):** commit hash, subject, file path, and line or diff context behind each claim, and what remains unproven.
- **Risk notes:** any history rewrites or force pushes.
- **Verification:** final `git status -sb` + `git log --oneline -n 5`.
- **Next steps:** push/PR guidance or follow-up questions.

## References

- Start with `references/README.md` for the index and summaries; load a playbook only when a step calls for it.
- External references are optional; use only if network access is permitted.
