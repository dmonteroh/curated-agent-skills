# Rebase and Conflict Resolution

## When to rebase

Use rebase to keep a feature branch clean and linear before merge (common for PR workflows).

Do not rebase if:
- the branch is shared and others have based work on it (unless coordinated)
- your repo intentionally preserves merge commits for context

## Safe rebase workflow

```sh
git fetch origin
git branch backup/$(git rev-parse --abbrev-ref HEAD)-before-rebase
git rebase origin/main
```

Interactive cleanup before PR:

```sh
git fetch origin
git branch backup/$(git rev-parse --abbrev-ref HEAD)-before-i
git rebase -i origin/main
```

Push rewritten history safely:

```sh
git push --force-with-lease
```

## Fold a fix into an earlier commit without an editor

`git rebase -i` opens a sequence editor and waits for it. Where no editor can be attached — a CI job, a git hook, a headless agent session — the command stalls or aborts instead of rewriting. Autosquash covers the common case with no editor at all:

```sh
git commit --fixup=<target-sha>
GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash <base>
```

- `git commit --fixup=<target-sha>` writes a commit whose subject is `fixup! <target subject>`.
- `--autosquash` reorders each `fixup!` commit directly under its target in the generated todo list.
- `GIT_SEQUENCE_EDITOR=:` replaces the sequence editor with a no-op, so that generated list is accepted exactly as written. This is what makes the operation available in a non-interactive environment.

Verify before pushing: `git log --oneline <base>..HEAD` should show no `fixup!` subjects left and the target commits rewritten.

An autosquash can still hit conflicts. Resolve them with the checklist below, then `git rebase --continue` — the no-op sequence editor does not change how conflicts are handled.

## Conflict resolution checklist

1) Identify conflicts
```sh
git status
```

2) Resolve intentionally (don’t blindly accept "theirs/ours")
```sh
git diff
```

3) Mark resolved and continue
```sh
git add <files>
git rebase --continue
```

4) If the strategy is wrong
```sh
git rebase --abort
```

Abort first, while the rebase is still in progress: it restores the pre-rebase branch tip and needs no reasoning about which SHA was correct. Reach for the reflog only once abort is unavailable because the rebase already finished — and state the intended recovery path, including the target SHA, before running anything that moves a ref (`references/recovery.md`).

## Common conflict footguns

- Resolving the same conflict repeatedly during rebase:
  - consider squashing earlier commits or using `git rerere` (reuse recorded resolution)
- Conflicts in lockfiles:
  - prefer regenerating lockfiles from a clean install rather than hand-editing
