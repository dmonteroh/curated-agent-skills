# Confirming the Skill Works

These scenarios validate the skill itself, not a single draft body. An operator runs them when material changes land in the skill or when output quality is in doubt. They are distinct from the workflow and output contract in `SKILL.md`: those validate one PR body; these scenarios validate that the skill reliably produces bar-passing bodies across representative input shapes.

1. **Two recent merged PRs with briefs.** Pick two recently merged pull requests from the target repository that shipped with task briefs. Run the skill against each branch state with the briefs supplied. Acceptance: each generated body matches the established PR quality bar without manual rewrites, the three required sections are present in order, and the verification playbook is appropriate to each PR's change type.

2. **No-brief change.** Run the skill against a small bugfix or refactor branch with no brief supplied. Acceptance: the generated body is appropriate to the weaker grounding, the *Why* section relies on commit messages and code intent rather than fabricated rationale, and the agent reply outside the body flags the weaker grounding and asks the user to confirm the *Why*.

3. **Mixed pull request sub-sectioning.** Run the skill against a branch that combines two concerns, for example a feature plus a migration. Acceptance: the classification is `mixed`, the playbook is split into labelled sub-sections with one recipe per concern, and an explicit independence note states whether the sub-sections may run in any order or have a required order.
