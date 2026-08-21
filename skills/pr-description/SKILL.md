---
name: pr-description
description: "Generates a paste-ready pull request description from task briefs and the branch diff against a base branch. Produces three required sections — What & Why, How, Manual Verification Playbook — with change-type-aware playbook recipes. Use when a pull request body needs to be drafted or refreshed."
metadata:
  category: git
---
# pr-description

Provides a deterministic workflow for producing a pull request body that meets a strict quality bar: three required sections in a fixed order, grounded in task briefs and the branch diff, with a change-type-aware manual verification playbook.

## Use this skill when

- The user asks for a pull request description, PR body, or "draft the PR" copy.
- A branch is ready for review and its description is missing, stale, or below the bar.
- The user supplies one or more task briefs and asks for a PR write-up grounded in them.

## Do not use this skill when

- The user asks to create the pull request on a hosting platform. This skill emits markdown only; the user pastes the output into their PR tool.
- The user asks to push the branch or run state-changing git commands. The skill only reads: `git diff`, `git log`, base-branch detection.
- The user asks for a commit message rather than a PR body. That is a commit-level task outside this skill.
- The user wants a per-file walkthrough or a changed-file inventory inside the body. The quality bar rejects both.

## Required inputs

- Current branch name (the branch under review).
- Base branch: user-specified, else the repository default (`git symbolic-ref refs/remotes/origin/HEAD`); if detection fails, ask.
- `git diff <base>...HEAD` and `git log <base>..HEAD --oneline` output. Always read both.
- Task brief(s) when available. Accepts one or more paths (umbrella plus child briefs are common).

## Defaults

- Output: a single markdown block, paste-ready, no surrounding commentary inside it.
- No additional top-level sections, no file inventories, no author attribution.
- Tone: factual, atemporal, impersonal, neutral.
- Spell out implementation acronyms on first use ("common table expression" rather than "CTE").

## Precedence rules

1. Explicit user constraints and wording.
2. Task brief content for intent and rationale.
3. Diff and log evidence for what the change actually does.
4. Branch and commit message hints as a fallback.

If signals conflict, follow higher-priority evidence and state the assumption in the agent reply.

## Workflow

### 1) Gather inputs

- Confirm the branch under review and the base branch.
- Read the diff and log against the base; they ground the *How* section and the playbook.
- Read every supplied task brief in full; briefs are the primary source for *What & Why*.
- If the diff against the base is empty: stop and report. There is no PR to describe.

Output: internal snapshot of branch, base, diff summary, commit subjects, and brief content.

### 2) Classify the change

Pick exactly one category and surface it before composing, so the user can correct it:

- `feature` — new user-visible capability, endpoint, UI flow, or reachable behavior.
- `bugfix` — defect or regression correction; a prior broken state exists to reproduce.
- `migration` — schema change, data-shape change, backfill, or anything that mutates persisted state.
- `pure-refactor-docs` — refactor, rename, dead-code removal, docs or comments only; no observable behavior change. Test-only changes proving existing behavior count here.
- `mixed` — two or more of the above, each needing its own playbook section.

Classification rules:
- Migrations dominate: any persisted-state change makes the PR `migration` or `mixed`, never plain `feature` or `bugfix`.
- A bugfix that also ships a new feature surface is `mixed`.
- When the diff is ambiguous, default to `mixed` rather than under-classifying.

### 3) Compose the three required sections

The body contains exactly these headings, in this order:

```
## What & Why

## How

## Manual Verification Playbook
```

**What & Why** — the change type, the problem or intent it serves (brief-grounded when possible), and who is affected: roles, surfaces, or flows by name. Two or three short paragraphs; bullets only when the impact list is genuinely a list.

**How** — concise prose grounded in the diff. Components, services, endpoints, and flows by name; no file paths; no commit-sequence narration. Describe the resulting system.

**Manual Verification Playbook** — a preamble (environment, prerequisites, tools by name, authentication or role notes, ordering note when multiple sections follow), then the recipe matching the classification. Read `references/playbook-recipes.md` and follow the matching recipe step by step. For `pure-refactor-docs`, emit the single not-applicable line; never invent steps. See `references/worked-examples.md` for the bar.

### 4) Apply step-level rules

Rewrite any playbook step that fails one of these:

- Every numbered step ends with an explicit *Expected result* or *Confirm* line. No naked actions.
- Concrete artifacts only: the real SQL statement, endpoint path, storage key, selector, or button label. Never "the relevant template" or "the appropriate row".
- Name the user role, token claim, table, column, or payload shape when the outcome depends on it.
- Cut steps that do not increase verification confidence. Signal is the goal, not length.
- No steps the reviewer cannot actually run with the listed tools and access.

### 5) Apply global writing rules

Apply to the entire body:

- Factual, relevant, necessary content only.
- Plain language; acronyms spelled out on first use.
- Atemporal: no "now", "currently", "after this change", "we just", or "previously" when describing the resulting system. Sole exception: bugfix repro steps contrasting the prior broken build with this build.
- Impersonal and neutral. Describe the change, not the author.

### 6) Handle missing briefs

- Compose *What & Why* from commit messages, code intent, and call sites.
- Flag the weaker grounding in the agent reply — never inside the body: name the assumption made about intent and ask the user to confirm the *Why* before pasting.

## Output contract

The PR body must contain exactly the three headings in order, be paste-ready, and satisfy the step-level and global writing rules.

The agent reply around the markdown block must include:

- Branch: `<branch>`
- Base: `<base>` (note if detected or overridden)
- Classification: `<feature|bugfix|migration|pure-refactor-docs|mixed>` with one-line evidence
- Briefs: `<paths or "none supplied; Why needs user confirmation">`
- Notes: assumptions or "none"

## Decision points

- If briefs and diff contradict on intent: follow the diff, surface the contradiction, and ask before treating the brief as authoritative.
- If multiple unrelated concerns land in one PR: produce a `mixed` body and note that splitting the PR may be cleaner.
- If the user supplies a non-default base: use it and state the override in the agent reply.

## Common pitfalls

- Drafting a confident *Why* without a brief and without flagging the gap to the user.
- Listing changed files or walking the diff file by file inside the body.
- Steps without assertions ("Open the page", "Run the migration") and vague artifacts ("the appropriate row").
- Acronyms left unexplained; time-stamped language describing the resulting system.
- Treating a migration-bearing PR as plain `feature` and skipping the baseline-and-post-state recipe.

## Self-check before emitting

Fix any failure before returning output:

1. Exactly three top-level headings, in order.
2. *What & Why* names the change type, the reason, and affected roles or surfaces.
3. *How* names components and contains no file paths.
4. The playbook preamble covers environment, prerequisites, tools, and authentication context.
5. The playbook follows the classification's recipe; `mixed` has labelled sub-sections and an ordering note.
6. Every step asserts; every artifact is concrete.
7. Global writing rules hold across the body.
8. No section lists changed files.
9. When no brief was supplied, the agent reply flags the weaker grounding and asks for confirmation.

## References

- Index: `references/README.md`
- Playbook recipes per change type: `references/playbook-recipes.md`
- Worked example bodies: `references/worked-examples.md`
- Operator validation scenarios: `references/skill-validation.md`
