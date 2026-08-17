# Apply prompt

Task: execute exactly one operator-approved removal from the skill library, and nothing else.

Dispatch context: this run is a dispatched subagent of the repository's review pipeline, and the orchestrator has already handled the CLAUDE.md/AGENTS.md session-bootstrap. Skip every bootstrap step - do not run .agent/scripts/status.sh, do not read .agent/ files - and begin the task immediately.

The operator has already ruled on this proposal; the decision is made. Do not re-litigate whether the removal is justified, and do not narrow it. Your job is a faithful, complete execution.

The proposal, as recorded from the review that made it:

PROPOSAL_TEXT

Operator note: RULING_NOTE

Rules:
- Write only inside SKILL_DIRECTORY and, where the proposal names it, scripts/auditing/trigger-cases/SKILL_NAME.md. Touch nothing else - no other skill, no docs, no scripts, no CHANGELOG, no catalog files; those are the operator's follow-up, not yours.
- Execute the removal in full: delete what the proposal names, and in the same pass update every reference to the removed content that lives inside SKILL_DIRECTORY - pointers in SKILL.md, rows in references/README.md, cross-links between reference files.
- Make no other improvement while you are there, however obvious it looks.
- If the removal cannot be executed coherently - the target is already gone, or deleting it would remove the file's last statement of a rule rather than a duplicate - make NO edit at all and end your final message with one flush-left line: APPLY-BLOCKED: <one-line reason>.
- Otherwise end your final message with one flush-left line: APPLIED: <changed file paths, comma-separated>.
