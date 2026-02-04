# Git Workflow Quick Cheatsheet

## Inspect

```sh
git status
git branch -vv
git log --oneline --graph --decorate -n 30
git show <sha>
```

## Sync with main safely

```sh
git fetch origin
git rebase origin/main
# or (if your repo prefers merge commits)
git merge origin/main
```

## Clean up commits before PR

```sh
git rebase -i origin/main
git push --force-with-lease
```

## Conflict resolution

```sh
git status
git diff
git add <resolved-files>
git rebase --continue   # or git merge --continue
git rebase --abort      # or git merge --abort
```

## Undo / recovery

```sh
git reflog
git reset --hard <sha>          # dangerous; prefer --mixed/--soft when possible
git restore --source <sha> -- <path>
git revert <sha>                # safe undo via new commit
```

## Cherry-pick

```sh
git cherry-pick <sha>
git cherry-pick <start>..<end>  # range
```

## Bisect

```sh
git bisect start
git bisect bad
git bisect good <known-good-sha-or-tag>
git bisect reset
```

