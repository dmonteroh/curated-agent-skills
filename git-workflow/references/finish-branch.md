# Finishing A Development Branch

This playbook is a pragmatic end-of-work routine: verify, then choose how to integrate.

## Preconditions

- You believe implementation is complete.
- You have a test command (or other verification command) that proves it.

## Step 1: Verify (non-negotiable)

Run the repo’s verification command(s) *fresh* and record the result.

Examples:

- `npm test`
- `pnpm -r test`
- `dotnet test`
- `go test ./...`
- `pytest`

If verification fails: stop and fix before integration.

## Step 2: Identify the base branch

Common: `main` or `master`. If unsure, ask or check:

```sh
git remote show origin | grep 'HEAD branch'
```

## Step 3: Choose one option

1) Merge locally
- Good when you control the repo state and want a direct merge.

2) Push and open a PR
- Default for team workflows.

3) Keep the branch as-is
- Good when you’re not ready to integrate.

4) Discard the work
- Only with explicit confirmation.

## Option 1: Merge locally

```sh
git checkout <base>
git pull --ff-only

git merge <feature-branch>

# Verify again on the merged result
<test command>

# Cleanup
# (Only delete the branch if merge + verification succeeded)
git branch -d <feature-branch>
```

## Option 2: Push and open a PR

```sh
git push -u origin <feature-branch>
```

PR body template:

```md
## Summary
- 

## Test Plan
- [ ] <command + result>

## Risk / Rollback
- 
```

(Use your hosting tooling to create the PR; exact commands vary.)

## Option 3: Keep as-is

- Report current branch name and status.
- Do not delete worktrees or branches.

## Option 4: Discard (danger)

Require explicit confirmation before destructive actions.

Safe approach:

- Create a backup branch first:
  - `git branch backup/<name>-$(date +%Y%m%d-%H%M%S)`
- Then delete only after confirmation.

## Red Flags

- Don’t merge/PR with failing tests.
- Don’t delete branches/worktrees without explicit confirmation.
- Don’t force-push unless explicitly requested.
