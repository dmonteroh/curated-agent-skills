Task: Review SKILL_DIRECTORY/SKILL.md against the binding quality bar and bring it to that bar. AUTHORITY_TASK

Dispatch context: this run is a dispatched subagent of the repository's review pipeline, and the orchestrator has already handled the CLAUDE.md/AGENTS.md session-bootstrap. Skip every bootstrap step - do not run .agent/scripts/status.sh, do not read .agent/ files - and begin the review immediately.

Read first, in this order:
- CHECKLIST_PATH - the binding bar. It outranks every other input.
- OPEN_ITEMS_PATH - calls already settled. Arguing against one of these is wrong, not thorough.
- GUIDANCE_PATH - depth behind the bar. Read the section you need when a judgment call is not obvious.
- SKILL_DIRECTORY/SKILL.md and everything else under SKILL_DIRECTORY/.

Scope: only files under SKILL_DIRECTORY. Do not edit anything outside it.

Every review runs a pruning pass and reports its result, including "nothing to cut". Removing text is a first-class outcome, not a failure to add value.
<!-- parity:removal-authority:start -->
- Delete without asking: a sentence that restates its own heading; a restatement of the frontmatter description; a second statement of a rule already made elsewhere in the same file; a vacuous heading qualifier such as (Deterministic), (Always), (best results); a workflow step whose only output is "report per the output contract".
- Propose, never execute: removing a whole section, a file under references/ or scripts/, the skill itself, or activation cues found in SKILL.md. Give the evidence and what would be lost; the operator rules on it. For activation cues, write the cue content directly into trigger-cases/<skill>.md - the one scoped exception to dispatch scope - and file a removal proposal for the SKILL.md-side text. Filing that proposal discharges the §1 obligation for that skill; the review proceeds to a normal verdict.
- A review that deletes forty lines and adds none is successful. So is one that changes nothing.
<!-- parity:removal-authority:end -->

Differentiation - report it, never act on it:
- Judge whether this skill changes what a frontier model would do unprompted. It earns its cost only with an opinionated house convention, a non-obvious process with real decision points, embedded tooling that makes behavior deterministic, or a correction for something models reliably get wrong.
- Report STRONG or WEAK with one line of evidence. A WEAK verdict is a flag for the operator. Do not delete or rewrite the skill because of it.

Rules:
AUTHORITY_RULE
- Keep the skill independent: it must never require another skill to be installed, and never check for one.
- Do not add brainstorming-gate or multi-agent dependencies.
- Do not modify package manifests or add dependencies (no package.json, lockfiles, pip installs).
- Keep activation cues and trigger tests out of SKILL.md.
- Avoid time-sensitive facts and external network assumptions.
- Structure follows the skill's job. Mandatory: the frontmatter contract, "Use this skill when", "Do not use this skill when". Every other section is earned - do not add one because other skills have it.
- Voice: third person for the frontmatter description and the opening framing; imperative for procedure steps. No personas.
- Write script paths skill-relative (scripts/x.sh), never repo-root style (SKILL_DIRECTORY/scripts/x.sh), which does not resolve once the skill is installed.
- If splitting references, add references/README.md as an index. Split when a reader does not need the material in line, not because a token count was crossed.
- Measure reference file size with tiktoken (cl100k_base) using VENV_PYTHON_PATH.
- If anything is ambiguous, STOP and output QUESTIONS on a line of its own. Do not guess.

<!-- parity:verdict-enum:start -->
Output, in this order:
- Files changed (or "none")
- Summary of edits, separating what was removed from what was added, with line counts
- REMOVAL PROPOSALS: numbered, each naming the file and section, the evidence, and what would be lost. Write "none" if there are none.
- DIFFERENTIATION: STRONG or DIFFERENTIATION: WEAK, followed by one line of evidence
- Verification run (if any)
- Exactly one final status line, alone on its own line: REVIEW_STATUS: NO-CHANGE, REVIEW_STATUS: CHANGED, or QUESTIONS. Alongside REVIEW_STATUS: NO-CHANGE or REVIEW_STATUS: CHANGED, always: the DIFFERENTIATION: line from §3 and a REMOVAL PROPOSALS: block from §4, written as none when there are none. QUESTIONS ends the review immediately; it carries neither DIFFERENTIATION nor REMOVAL PROPOSALS.

Record this review's result by running, exactly once, when the review is finished:
- For REVIEW_STATUS: NO-CHANGE or REVIEW_STATUS: CHANGED: RESULT_TOOL_PATH --status <no-change|changed> --read-proof "<line CHALLENGE_LINE of SKILL_DIRECTORY/SKILL.md, reproduced verbatim on this same line>" --differentiation <strong|weak> --removals "<none, or a short summary that removal proposals exist>"
- For QUESTIONS: RESULT_TOOL_PATH --status questions --read-proof "<line CHALLENGE_LINE of SKILL_DIRECTORY/SKILL.md, reproduced verbatim on this same line>"

Running that command is what files the review result. A status written in prose above is commentary for the reader and is filed nowhere, so a review that only writes prose leaves no result on record.
<!-- parity:verdict-enum:end -->
