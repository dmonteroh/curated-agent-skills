---
name: changelog-automation
description: "Automate changelog and release note generation from commits or PR metadata using Keep a Changelog and semantic versioning. Use when designing release workflows or standardizing commit conventions."
category: workflow
---
# Changelog Automation

Provides patterns and tools for automating changelog generation, release notes, and version management.

## Use this skill when

- Setting up automated changelog generation
- Implementing conventional commits
- Creating release note workflows
- Standardizing commit message formats
- Managing semantic versioning

## Do not use this skill when

- The project has no release process or versioning
- You only need a one-time manual release note
- Commit history is unavailable or unreliable

## Required inputs

- Repository context (commits, PRs, or labels)
- Target changelog format and versioning strategy
- Release cadence and publication target (e.g., file-only vs. release page)
- Tooling constraints (language runtime, CI provider)

## Constraints

- Avoid assuming network access unless explicitly required.
- Keep the workflow self-contained without requiring other skills.

## Instructions

1. Confirm the source of truth (commits vs. PR labels) and release scope.
   - Output: one-paragraph summary of the data source and release scope.
   - Decision: if commit messages are inconsistent, plan label-based mapping instead.
2. Choose a changelog format and versioning rules.
   - Output: selected format (e.g., Keep a Changelog) and version bump rules.
   - Decision: if a changelog already exists, align to its section headings.
3. Define classification rules (commit types or labels to sections).
   - Output: a mapping table of change types → changelog sections.
4. Pick an automation approach and list required files.
   - Output: tool choice, config files to add/update, and required tools or plugins.
   - Decision: if CI is unavailable, document a local release script instead.
5. Generate a preview and validate contents.
   - Output: preview summary with missing items or sensitive data to redact.
6. Publish the changelog/release notes plan.
   - Output: ordered steps to update `CHANGELOG.md`, tag releases, and publish notes.

## Common pitfalls

- Mixing unrelated changes in one commit makes sections inaccurate.
- Missing breaking-change markers leads to incorrect version bumps.
- Editing generated changelogs manually causes drift from automation.
- Exposing internal ticket IDs or secrets in release notes.

## Safety

- Avoid exposing secrets or internal-only details in release notes.

## Examples

**Input**
"Set up automated release notes from conventional commits in GitHub Actions."

**Output**
- Summary: Automate release notes from `main` using conventional commits.
- Decisions: Keep a Changelog with Added/Changed/Fixed; semantic-release workflow.
- Files/Configs: `release.config.js`, `.github/workflows/release.yml`.
- Commands: `npx semantic-release --dry-run`.
- Verification: Compare generated notes to commit history.
- Risks/Follow-ups: Confirm release permissions and secrets.

## Output contract

- Chosen format, versioning rules, and classification mapping.
- Automation approach with files and commands to add/update.
- Verification steps for previewing the changelog.
- Risks, gaps, or follow-up decisions needed.
- Reporting format populated as specified below.

## Reporting format

- Summary: ...
- Decisions: ...
- Files/Configs: ...
- Commands: ...
- Verification: ...
- Risks/Follow-ups: ...

## References

- `references/README.md` for detailed patterns, templates, and configurations.
