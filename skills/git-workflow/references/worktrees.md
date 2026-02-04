# Worktrees (Parallel Branch Work)

Worktrees let you work on multiple branches at once without stashing or switching.

## Recommended convention (avoid pollution)

- Prefer a consistent worktree root directory (commonly `.worktrees/`).
- If using a project-local worktree directory, ensure it is ignored by git to avoid accidental tracking.

Safety gate (project-local):

```sh
git check-ignore -q .worktrees || git check-ignore -q worktrees
```

If not ignored, stop and explicitly decide whether to update `.gitignore`.

## Basic commands

```sh
git worktree list
git worktree add ../repo-hotfix hotfix/urgent
git worktree add -b feature/new ../repo-feature origin/main
git worktree remove ../repo-hotfix
git worktree prune
```

Safety tips:
- Each worktree has its own working directory; commits are shared.
- Remove worktrees you no longer need to avoid confusion.

## Baseline verification (high-signal habit)

Inside a new worktree:

```sh
git status --porcelain
```

If the repo has standard checks, run them to establish a clean baseline (only if appropriate for the environment).
