---
name: using-git-worktrees
description: Create isolated git worktrees safely (directory conventions, ignore verification, baseline checks) so parallel work does not pollute the main workspace. Works standalone; no dependencies on other skills.
---

# Using Git Worktrees

Git worktrees let you work on multiple branches simultaneously with isolated working directories.

## Use this skill when

- Starting a feature that should not disrupt your current workspace
- Running parallel experiments, reviews, or builds on separate branches
- You need a clean baseline to distinguish pre-existing failures from new ones

## Do not use this skill when

- The repo is not a git repository
- You cannot create new directories in the working environment

## Workflow (Deterministic)

1) Choose a worktree root directory
- Prefer an existing convention if the repo documents one (AGENTS.md/README/CLAUDE.md).
- Otherwise use a project-local directory (commonly `.worktrees/`).

2) Safety gate (project-local worktrees)
- Verify the worktree root is ignored by git before creating worktrees.
- If it is not ignored, stop and ask before changing ignore rules.

3) Create the worktree
- Create a new branch (or attach existing) and add the worktree directory.

4) Baseline verification
- Confirm `git status` is clean in the worktree.
- Run the project’s standard checks (tests/build) only if available and appropriate.
  - Do not install dependencies or run networked commands without approval.

## Output Contract (Always)

- Worktree path and branch name
- What safety checks were performed (ignore verification, baseline status)
- What verification was run (or explicitly skipped, with reason)

## Resources (Optional)

- Implementation playbook (commands + checklists): `resources/implementation-playbook.md`

