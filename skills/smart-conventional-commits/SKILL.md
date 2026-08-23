---
name: smart-conventional-commits
description: "Create high-quality conventional commits from working-tree changes and user intent: inspect-first safe staging, repo-convention detection from git history, branch-aware type and scope inference, and strict title/body formatting. Use when users ask to commit changes or draft commit messages."
metadata:
  category: git
---
# smart-conventional-commits

Provides a deterministic workflow for turning working-tree changes and user intent into well-formed conventional commits that match the conventions the repository already uses.

## Use this skill when

- The user asks to create a commit, commit staged or unstaged changes, or draft a commit message.
- The user provides intent text that should shape the commit title or body.
- A completed change needs to be committed and the user has asked for it.

## Do not use this skill when

- The user explicitly asks for a non-conventional commit format. Follow their format instead.
- There are no changes to stage or commit. Report the clean tree instead.
- The user asks only for history review, or for rewriting commits that are already pushed.

## Required inputs

- User request text (intent, constraints, any wording that must be preserved).
- `git status --porcelain` output and the diff that will be committed.
- Current branch name and recent history (`git log --oneline -30`).

## Defaults

- Title and body are both mandatory. Body stays concise (usually 1-3 lines).
- Standard conventional types unless the repository documents or uses custom types.
- No footers, trailers, or issue references unless confirmed by the user or established in repo convention.

## Precedence rules

1. Explicit user constraints and wording.
2. Documented repo conventions (commitlint/commitizen config, commit template, CONTRIBUTING).
3. Patterns in recent commit history (types, scopes, casing, language, trailers).
4. Staged diff semantics and changed paths.
5. Branch-name hints (`feature/*`, `fix/*`, `docs/*`, ...).

When signals conflict, follow the higher-priority evidence and state the assumption in the report.

## Workflow

### 1) Inspect state before touching the index

Actions:
- Read `git status --porcelain` and the current branch name.
- If the index already contains a deliberate subset of changes, treat that subset as the commit candidate; do not stage anything else without asking.
- Otherwise, plan a staging set covering the changes relevant to the request.
- If there is nothing to commit, stop and report the clean tree.

Output: commit candidate (existing index or planned staging set) plus branch context.

### 2) Stage safely

Actions:
- Stage the planned set with explicit paths; use `git add -A` only after confirming from status output that everything in the tree belongs to the request.
- Hold back and surface suspicious paths instead of staging them: secrets and credentials (`.env`, keys, tokens), build artifacts and caches, vendored dependencies, large binaries, and editor or OS junk not covered by `.gitignore`.
- Read the staged diff (`git diff --cached`). This diff, not the working tree, is what the message must describe.

Output: staged snapshot plus a list of anything deliberately held back and why.

### 3) Detect repo conventions

Actions:
- Scan `git log --oneline -30` for the convention in use: types and scopes seen, description casing, language, ticket prefixes, trailer habits.
- Check for commitlint/commitizen config or a commit template; documented rules beat history patterns.
- If history is not conventional-commit shaped at all, say so and confirm before introducing the format.

Output: the convention profile the message must match.

### 4) Infer type and scope

Type rules (first match wins):
- `docs` / `test` / `ci` / `build`: the change touches only that concern.
- `fix`: corrects broken or regressed behavior.
- `feat`: adds capability or user-visible behavior.
- `perf`: performance-focused change without behavior change.
- `refactor`: structural change without intended behavior change.
- `chore`: maintenance that fits none of the above.

Branch hints bias inference but never override diff evidence: `feat/*` and `feature/*` bias toward `feat`; `fix/*`, `hotfix/*`, `bugfix/*` toward `fix`; `docs/*` toward `docs`. A docs-only diff stays `docs` even on a feature branch.

Scope rules: use the dominant module, package, or path segment when one clearly dominates and the repo uses scopes; omit otherwise. Reuse scope names from history; never invent near-duplicates of existing scopes (`api` vs `apis`).

Output: inferred type and optional scope, with confidence.

### 5) Draft title and body

Title:
- `<type>(<scope>): <description>` or `<type>: <description>`.
- Imperative mood ("add", not "added" or "adds"), 72 characters maximum, no trailing period, lowercase description start unless a proper noun leads.
- Preserve the user's key nouns and verbs; rewrite around them for clarity.
- Describe the effect, not the mechanics ("prevent duplicate form submits", not "add if check to handler").

Body:
- Blank line after the title. Explain why, plus the notable what; never restate the file list.
- Bullets for multiple distinct points; one sentence for a single point.

Footers:
- Breaking change: append `!` after the type/scope and add a `BREAKING CHANGE: <user impact>` footer.
- Issue references (`Closes #123`) only when the user confirms or repo convention demands and the identifier is certain.
- No tool-attribution or co-author trailers unless repo history uses them or the user asks.

Output: draft conventional title and body.

### 6) Safety checks, commit, report

Checks before committing:
- Mixed docs+code changes: prefer the code-oriented type.
- Unrelated concerns in one diff: propose a split with concrete per-commit path groups; commit best-effort in one commit only if the user already chose that.
- Low confidence in type, scope, or meaning: show the draft and ask before committing.

Commit behavior:
- Commit with the validated title and body.
- If a pre-commit hook rewrites files: restage exactly the hook-modified files and retry once.
- If a hook fails: report the failure and stop. Never pass `--no-verify` unless the user explicitly asks.
- Amend only when the user requests it; if the target commit is already pushed, warn and get confirmation first.

Output: created commit hash and final message, or the clarification question that blocked the commit.

## Decision points

- If the user asks for a custom type: use it only when documented in-repo or present in history; otherwise propose the nearest standard type.

## Examples

Input: "commit unstaged changes" on branch `feature/on-demand-download`; the diff adds a UI button and a handler calling the export endpoint; an untracked `debug.log` is present.

Output:
- Branch: `feature/on-demand-download`
- Staged: `git add src/ui src/handlers` (2 files); held back `debug.log` (untracked scratch)
- Title: `feat(export): add on-demand PDF download button`
- Body: Let users trigger the PDF export from the detail view instead of waiting for the nightly batch.
- Commit: `<hash>`
- Notes: History uses scoped types; scope `export` appears in 6 recent commits.

Input: "commit this as a hotfix" with a docs-only diff on branch `hotfix/typo`.

Output:
- Title: `docs: fix typo in install instructions`
- Notes: Docs-only diff overrides the branch hint toward `fix`; stated the override.
