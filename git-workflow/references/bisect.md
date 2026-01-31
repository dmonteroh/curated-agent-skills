# Bisect (Find the Regression Commit)

Use when you know:
- a "good" commit (or tag)
- a "bad" commit (often HEAD)

## Manual bisect

```sh
git bisect start
git bisect bad
git bisect good <known-good-sha-or-tag>

# run your test manually, then:
git bisect good
# or:
git bisect bad

git bisect reset
```

## Automated bisect

`git bisect run` expects a script that exits:
- 0 for good
- 1..127 for bad (except 125)
- 125 to skip

```sh
git bisect start HEAD <known-good-sha-or-tag>
git bisect run ./scripts/test.sh
git bisect reset
```

