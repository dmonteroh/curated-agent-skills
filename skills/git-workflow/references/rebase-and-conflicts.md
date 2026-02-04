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

4) If you realize the strategy is wrong
```sh
git rebase --abort
```

## Common conflict footguns

- Resolving the same conflict repeatedly during rebase:
  - consider squashing earlier commits or using `git rerere` (reuse recorded resolution)
- Conflicts in lockfiles:
  - prefer regenerating lockfiles from a clean install rather than hand-editing

