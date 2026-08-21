# Auditing Scripts

This folder contains the skill review checklist, the parallel review runner, and supporting artifacts.

## Setup: tiktoken required for token checks

Token checks require `tiktoken`. The recommended way to run the audit installs it automatically:

```bash
./scripts/audit-skills.sh
```

If you want to run the audit directly:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements-audit.txt
.venv/bin/python scripts/audit_skills.py
```

To explicitly skip token checks:

```bash
./scripts/audit-skills.sh --no-token-checks
```

## Parallel skill reviews

The parallel reviewer installs the same audit dependencies automatically and uses the repo `.venv`:

```bash
./scripts/auditing/run_parallel_skill_reviews.sh
```

Pipeline behavior:

1. Per skill, the default pipeline dispatches one read-only review per declared arm, then a synthesis call applies the single change that lands. `--arms <name>[,<name>...]` selects the reviewer arm set (default: `codex,claude`); every arm stays read-only and synthesis stays the run's only writer regardless of arm count.
2. Every arm must prove it read the skill: its verdict carries a `READ_PROOF` line reproducing a challenge line the runner picked from that skill's `SKILL.md`. An absent or mismatched proof fails the arm and blocks the skill from synthesis. The comparison whitespace-strips both sides and unwraps a wholly backtick-wrapped value — an arm is never failed for reproducing indentation verbatim.
3. Runner runs `scripts/audit_skills.py` unconditionally once all subagents complete.

Useful options:

```bash
# Preview selected work without running subagents
./scripts/auditing/run_parallel_skill_reviews.sh --dry-run

# Run a smaller custom batch
./scripts/auditing/run_parallel_skill_reviews.sh --batch-size 4

# Target a subset
./scripts/auditing/run_parallel_skill_reviews.sh --skill testing --skill deps-audit

# List discovered skills
./scripts/auditing/run_parallel_skill_reviews.sh --list-skills

# Print the model-tier resolution table and exit
./scripts/auditing/run_parallel_skill_reviews.sh --print-model-policy

# Run with a single reviewer arm (e.g. one client temporarily unavailable)
./scripts/auditing/run_parallel_skill_reviews.sh --arms claude
```

`--print-model-policy`'s own policy header states the pipeline's tier policy: sol/opus unused in this pipeline; terra for dispatches that need reasoning; luna otherwise (operator policy, 2026-08-12).

### Multi-model review

Default invocation — no flag needed, this is the default pipeline:

```bash
./scripts/auditing/run_parallel_skill_reviews.sh
```

Multi-arm review is the standard review pass for every skill in the library; `--arms <name>[,<name>...]` is how a human deliberately selects a different arm set.

Call count: N reviewer arms plus one synthesis call per skill (N+1). Today's arm declaration (`REVIEWER_ARMS`) holds 2 arms, so N+1 = 3 calls per skill; a full run over all 95 skills in `skills_list.txt` is 285 calls. Re-count `skills_list.txt` rather than trusting this figure — the library grows.

## What Each File Does

- `SKILL_REVIEW_CHECKLIST.md`
  - The binding quality bar for skill content; always loaded by reviewers, and it outranks the resources below.
  - Covers the frontmatter contract, the use/do-not-use boundary, differentiation, mandatory subtraction, earned structure, voice, executable instructions, references, budgets, and independence.

- `references/authoring-guidance.md`
  - Depth behind the bar, read on demand: the pruning taxonomy, a worked differentiation contrast, over-constraint, leading words, teach-by-contrast, behavioral gates, and the patterns this library rejects on purpose.

- `OPEN_ITEMS.md`
  - Settled calls a reviewer must not re-open, the parity register for deliberately duplicated blocks, deferred lints, and trial-gated removal candidates.

- `run_parallel_skill_reviews.sh`
  - Spawns parallel subagent reviews (10 per batch by default).
  - Dispatches one read-only reviewer arm per entry in `REVIEWER_ARMS` (`--arms` selects the set), then one synthesis call that is the run's only writer; applied changes, subtraction included, land under the skill folder at that synthesis step.
  - Reviewer arms run at `medium` reasoning effort by default — `--effort` overrides (claude arm via `--effort`, codex arm via `-c model_reasoning_effort`); the codex arm always pins `-c service_tier=default` so priority (speed) processing stays off; `--synthesis-effort` sets the synthesis call's effort (unset by default).
  - Reaps the `KEY=VALUE` verdict file each arm writes via `review-result.sh` (`OUTCOME`, `DIFFERENTIATION`, `REMOVAL_PROPOSALS`), and summarizes weak-differentiation and removal-proposal skills for the operator; proposal text is recorded to `PROPOSALS.md` via `proposals.py record`.
  - Runs `scripts/audit_skills.py` unconditionally after all subagents complete.
  - Supports targeting specific skills and dry-run planning.
  - Reports per-skill success/failure with log paths.
  - Measures reference size via `tiktoken` to decide when to split/index references.

- `review-result.sh`
  - The tool every arm executes to record its verdict. Validates `--status`, `--differentiation`, `--removals` and the optional `--read-proof`, then writes `OUTCOME=`, `DIFFERENTIATION=`, `REMOVAL_PROPOSALS=` and `READ_PROOF=` to `$REVIEW_RESULT_FILE`.
  - When `$REVIEW_REMOVALS_FILE` is set (the runner sets it on the synthesis call only), a real removals block is written there verbatim; `none` and `--status questions` clear any stale copy.
  - Last call wins: a re-invocation replaces the file rather than appending, and a rejected call leaves the previous contents intact.

- `proposals.py`
  - The removal-ruling loop. `record` (run by the runner after a pass with proposals) appends each proposal from the `<skill>.synthesis.removals` artifacts to `PROPOSALS.md`, one entry per numbered item, deduplicated by content hash against the ledger and the ids already ruled in `OPEN_ITEMS.md`.
  - `lint` validates every entry — ruling is `pending`/`approved`/`declined`, text matches its checksum — and reports all problems at once.
  - `apply` lints first and refuses to act on any problem. Declined entries become rows in `OPEN_ITEMS.md` "Removal rulings"; each approved entry gets one writer dispatch (`apply-prompt.md`; model from the runner's `--print-model-policy` synthesis site, overridable via `--dispatch-cmd`), its diff verified non-empty and inside the skill's own surface, then its row appended and the entry cleared. A rerun is a no-op for everything already resolved; pending entries are never touched.

- `PROPOSALS.md`
  - The pending-rulings ledger, machine-managed by `proposals.py`; holds only entries awaiting a ruling. The operator edits exactly one thing: each entry's `ruling:` line.

- `apply-prompt.md`
  - The writer prompt for one approved removal: scoped to `SKILL_DIRECTORY` plus the skill's own trigger-case file, forbidden from re-litigating the ruling, and required to end with `APPLIED:` or `APPLY-BLOCKED:`.

- `review_log.py`
  - Infra-banner detection only. `classify()` takes log text and returns `Classification(outcome=…)`, where `Outcome` is exactly `MALFORMED` or `INFRA-FAILURE`; prose verdict resolution was retired, and the verdict itself comes from the `review-result.sh` file the arm writes.
  - Pure text-in/value-out: no filesystem, network, or subprocess access, and importing it has no side effects.

- `reviewer-prompt.md`
  - Read at each reviewer arm's dispatch: the discovery contract, mandatory subtraction, differentiation, rules, and the Output verdict block.
  - Placeholders (`SKILL_DIRECTORY`, `CHECKLIST_PATH`, `GUIDANCE_PATH`, `OPEN_ITEMS_PATH`, `VENV_PYTHON_PATH`, `AUTHORITY_TASK`, `AUTHORITY_RULE`, `CHALLENGE_LINE`) are interpolated by the runner before dispatch.

- `synthesis-prompt.md`
  - Read at the synthesis call: the tie-break chain that resolves disagreement between reviewer arms, the vendor-agnostic framing block, and the sole per-skill write authority in a multi-arm run.
  - Placeholders (`SKILL_DIRECTORY`, `SKILL_NAME`, `CHECKLIST_PATH`, `OPEN_ITEMS_PATH`, `REVIEW_ARTIFACTS`) are interpolated by the runner before dispatch.

- `references/agent_skills_pdf.txt`
  - Extracted text from the reference PDF, kept for provenance. Not given to dispatched reviewers (`OPEN_ITEMS.md`, settled 2026-08-16).

- `logs/`
  - Subagent execution logs per skill.

- `trigger-cases/`
  - Per-skill activation test prompts.
  - Not referenced from `SKILL.md` to avoid runtime token overhead.

## Decisions (Rationale)

### Checklist rules

- **Tool-style language**: Skills are a knowledge/method layer, not an agent persona. Since 2026-08-11 the framing stays third person while procedure steps may use the imperative.
- **Trigger cases**: Keeps activation test prompts out of `SKILL.md`, in `trigger-cases/`, for predictable and repeatable activation behavior.
- **Structured workflow**: Step outputs + decision points prevent ambiguous execution. Structure beyond the frontmatter contract and the use/do-not-use boundary is earned by the skill's job, not imposed by a template.
- **Reference decomposition**: Long or multi-topic references are split and indexed to keep SKILL.md concise and navigable.
- **Subtraction**: Reviews must prune. Removing text is a first-class outcome, bounded by the closed five-item list in `SKILL_REVIEW_CHECKLIST.md` §4; whole sections, reference files, and whole skills are proposed for the operator rather than removed.

### Reference indexing threshold

- Index when there are **2+ reference files**. Route material into `references/` when a reader does not need it in line — not because a token count was crossed.

### Token checks

- Token measurement is mandatory by default. Use `--no-token-checks` only when you need a fast, dependency-free run.

### Runner defaults

- Batch size defaults to `10`.
- The runner auto-discovers skills under `skills/*/SKILL.md`.
- Pass `--skill <name>` one or more times to restrict scope.
- `scripts/audit_skills.py` runs unconditionally after subagent updates complete.

## Logs and Gitignore

If you add `scripts/auditing/logs/` to `.gitignore`, local tools and agents will still be able to read and use the logs; they simply won’t be committed to git.

## When to Regenerate agent_skills_pdf.txt

`agent_skills_pdf.txt` is derived from the reference PDF (Richard Hightower's article referenced below). Keep it if you want offline, deterministic access to the reference text. It can be regenerated at any time from the PDF if needed.

## References

These sources informed the checklist and review process:

```
https://medium.com/@richardhightower/agent-skills-the-universal-standard-transforming-how-ai-agents-work-fc7397406e2e
https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
https://cursor.com/docs/context/skills
https://agentskills.io/what-are-skills
https://developers.openai.com/codex/skills/
```
