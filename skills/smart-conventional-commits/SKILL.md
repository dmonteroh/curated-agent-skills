---
name: smart-conventional-commits
description: "Create conventional commits from user intent and git diff context, including auto-staging, branch-aware type inference, and concise mandatory title/body generation. Use when users ask to commit changes or draft commit messages."
category: git
---
# smart-conventional-commits

Provides a deterministic workflow for creating high-quality conventional commits from working tree changes and user intent.

## Use this skill when

- The user asks to create a commit, draft a commit message, or "commit unstaged changes".
- The user provides intent text that should appear in the commit title/body.
- The agent needs branch-aware type inference for conventional commits.

## Do not use this skill when

- The user explicitly asks for a non-conventional commit format.
- The repository has no changes to stage or commit.
- The user asks only for git history review without creating a commit.

## Required inputs

- User request text.
- Repository working tree and index state.
- Current branch name.

## Defaults

- Stage all changes with `git add -A`.
- Title is mandatory.
- Body is mandatory and concise (adaptive length, usually 1-3 lines).
- Use standard conventional types unless custom types are documented in-repo.

## Precedence rules

1. Explicit user constraints and wording.
2. Staged diff semantics and changed paths.
3. Branch-name hints (`feature/*`, `fix/*`, `docs/*`, etc.).
4. Fallback heuristics.

If signals conflict, follow higher-priority evidence and state assumptions.

## Workflow

### 1) Prepare commit candidate

Output:
- Staged snapshot and branch context.

Actions:
- Stage all modified, deleted, and untracked files.
- Read staged diff and changed file paths.
- Detect empty diff; stop and report if nothing to commit.

### 2) Infer type and scope

Output:
- Inferred type and optional scope with confidence.

Type rules:
- `feat`: new capability or user-visible behavior.
- `fix`: bug or regression correction.
- `docs`: docs-only change.
- `test`: test-only change.
- `refactor`: structural change without intended behavior change.
- `perf`: performance-focused change.
- `build`/`ci`/`chore`: tooling or maintenance work.

Branch hints:
- `feature/*` and `feat/*` bias toward `feat`.
- `hotfix/*`, `fix/*`, and `bugfix/*` bias toward `fix`.
- `docs/*` biases toward `docs`.
- Docs-only changes stay `docs` even on feature/fix branches.

Scope rules:
- Use dominant module/path when clear.
- Omit scope when unclear.

### 3) Draft title and body

Output:
- Conventional title and concise body.

Formatting:
- `<type>(<scope>): <description>` or `<type>: <description>`.
- Keep user intent keywords in the message when provided.
- Rewrite for clarity without losing requested meaning.
- Keep tone human and direct; avoid filler.

Example mapping:
- User intent: "create a commit, on demand button for downloading pdf"
- Candidate: `feat: add on-demand PDF download button`

### 4) Apply safety checks

Output:
- Final commit message or clarification question.

Checks:
- If confidence is low, ask user to confirm before committing.
- For mixed docs+code changes, prefer code-oriented type unless docs-only.
- If branch/issue naming suggests footers (for example refs), ask the user before adding trailers.
- Detect breaking changes and add `!` and/or `BREAKING CHANGE:` when clearly justified.

### 5) Commit and report

Output:
- Created commit hash and final message.

Actions:
- Commit using inferred and validated title/body.
- Report exactly what was committed and any assumptions made.

## Decision points

- If empty diff after staging: do not commit.
- If multiple unrelated concerns are detected: either proceed with best effort or ask user to split.
- If user asks for custom type: use it only when documented in-repo; otherwise propose standard type.

## Common pitfalls

- Losing key user nouns/verbs when rewriting the title.
- Overusing branch hints when diff evidence says otherwise.
- Generating vague titles such as "update files".
- Adding unconfirmed issue footers automatically.

## Output contract

Always report:
- Branch name used.
- Staging command performed.
- Final commit title.
- Final commit body.
- Commit hash (if created).
- Any user confirmation requested due to low confidence.

Reporting format:
- Branch: <branch>
- Staging: <command/result>
- Title: <title>
- Body: <body>
- Commit: <hash or "not created">
- Notes: <assumptions or "none">

## Examples

Input:
- "commit unstaged changes"

Output:
- Branch: `feature/on-demand-download`
- Staging: `git add -A` completed
- Title: `feat: add on-demand PDF download button`
- Body: Added a UI action to trigger PDF download on demand.
- Commit: `<hash>`
- Notes: Branch and diff both indicated a feature change.
