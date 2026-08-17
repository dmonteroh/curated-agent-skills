# Recovery (Undo Mistakes Safely)

## Prefer safe undo first

- Undo a commit by adding a new commit:
  - `git revert <sha>`

This preserves history and is usually the right approach for shared branches.

## Reflog: find "lost" commits

```sh
git reflog
```

Recover a deleted branch tip:

```sh
git branch recovered/<name> <sha-from-reflog>
```

The reflog is not permanent storage. `git gc` expires reflog entries, and entries pointing at commits nothing else reaches — exactly the case after a hard reset or a deleted branch — expire on a shorter schedule than reachable ones. Both windows are set by `gc.reflogExpireUnreachable` and `gc.reflogExpire` and are configurable per repo, so read the repo's own values with `git config --get gc.reflogExpireUnreachable` rather than assuming a default. Treat recovery as time-limited: create the recovery branch as soon as the lost SHA is identified, rather than leaving it in the reflog.

## Reset modes (know what they do)

- `--soft`: keep changes staged
- `--mixed` (default): keep changes unstaged
- `--hard`: discard changes in working tree (dangerous)

Common workflows:

```sh
# Move HEAD back but keep changes to recommit differently
git reset --soft HEAD~1

# Unstage everything but keep working tree changes
git reset
```

## Restore a file from another commit

```sh
git restore --source <sha> -- path/to/file
```

## Uncommit a pushed commit (shared branch)

If the commit is already in a shared branch, prefer revert:

```sh
git revert <sha>
git push
```

