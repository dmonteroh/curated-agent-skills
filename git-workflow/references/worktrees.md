# Worktrees (Parallel Branch Work)

Worktrees let you work on multiple branches at once without stashing or switching.

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

