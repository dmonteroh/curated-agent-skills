# Open items and settled calls

Reviewers re-litigate the same judgment calls every run and have no memory between runs. This file is that memory. Read it before ruling on anything the checklist leaves to judgment.

Source pattern: the operator's `ai-workflows` → `workflows/conventions.md` ("Open Items", parity register, trial-gated removal).

## Settled calls — do not re-open

A review that argues against one of these is wrong, not thorough. Bring new evidence to the operator instead.

| Date | Call |
| --- | --- |
| 2026-08-11 | **Structure is bounded, not fixed.** Mandatory: the frontmatter contract and both boundary sections. Every other section is earned by the skill's job. The old mandatory skeleton is withdrawn. |
| 2026-08-11 | **Voice is split.** Imperative for procedure steps; third person for the frontmatter `description` and the opening framing. Personas remain banned. |
| 2026-08-11 | **Removal authority is split.** A reviewer deletes on its own only the five items closed by `SKILL_REVIEW_CHECKLIST.md` §4 — glossed here as intra-file no-ops, heading restatements, and duplicates, granting nothing beyond that closed set. Whole sections, files under `references/` or `scripts/`, and whole skills are proposed with evidence and never executed. The operator has the last call on every removal. |
| 2026-08-12 | **Checklist-vs-settled-call conflicts are reported, not adjudicated.** The checklist outranks background and vendored guidance (`references/authoring-guidance.md`, `resources/`) — `SKILL_REVIEW_CHECKLIST.md:3`. Settled calls recorded in this file are not "other guidance": they are recorded operator decisions on judgment the checklist leaves open, and line 9 above still governs disagreement with them. Where the checklist's current text and a settled call genuinely contradict, that is a defect in the bar: the reviewer applies neither, reports the conflict naming both `file:line` anchors, and the operator rules. |
| 2026-08-11 | **Differentiation is a flag.** `DIFFERENTIATION: WEAK` is reported with evidence and acted on by nobody but the operator. It is not a removal trigger. |
| 2026-08-11 | **Repair versus re-author is the reviewer's call**, per skill, within the removal authority above. |
| 2026-08-11 | **The bar is three files**: `SKILL_REVIEW_CHECKLIST.md` (binding, always loaded), `references/authoring-guidance.md` (depth, read on demand), this file (memory). |
| standing | **A skill never requires another skill** to be installed, and never checks for one. Founding constraint; not a trade-off to revisit. |
| standing | **Activation cues stay in `trigger-cases/`**, never in `SKILL.md`. Frontmatter must load identically across Codex, Claude, and Copilot. |
| standing | **Prose is soft-wrapped**, one line per paragraph or list item. The divergence from `dot-agent` and `ai-workflows`, which hard-wrap, is deliberate. |
| standing | **`mattpocock/skills` is evaluation input only.** Reimplement patterns in this repo's words with a citation; never copy their text. |
| standing | **`ai-workflows` stays a separate repository.** Its techniques are reimplemented and cited here; its files are never vendored. Three role prompts vendored into `subagent-orchestrator` in Feb 2026 drifted until one contradicted its upstream, and were retired 2026-08-11. |
| 2026-08-11 | **A skill describes the properties an artifact needs; it does not carry another repository's templates.** `subagent-orchestrator` states what a complete worker packet contains and cites `ai-workflows` as a source to adapt from. Copying templates across a repo boundary with no sync mechanism is the failure this replaces. |
| 2026-08-16 | **Multi-arm review is the standard review pass for every skill in the library** (N reviewer arms, then one synthesis call), at N+1 calls per skill — 3 per skill, 165 for a 55-skill pass at today's two arms. `--single-model` is an exception a human selects deliberately. |
| 2026-08-16 | **Every reviewer arm is read-only and advisory; the synthesis agent is the sole writer** in a multi-arm run, holding exactly the existing single reviewer's authority (`SKILL_REVIEW_CHECKLIST.md` §4, `SUBAGENT_REVIEW_PROCESS.md` "Removal authority"). |
| 2026-08-16 | **The tie-break rule** governing synthesis is `synthesis-prompt.md`'s "Tie-break chain": a finding is actionable only if it cites a specific checklist section and is verifiable in the skill file; among grounded, conflicting positions subtraction wins, applying the union of every review's grounded cuts, narrowed only so the union never deletes the last statement of a rule; a conflict the union does not settle ends the run with `QUESTIONS`. |
| 2026-08-16 | **The pipeline has no anonymization stage.** Vendor-agnostic framing plus the requirement that every applied finding cite the checklist section it rests on is what replaces it, owned by `synthesis-prompt.md`. |
| 2026-08-16 | **Model-tier policy** (operator policy 2026-08-12): `sol`/`opus` unused in this pipeline; `terra` for dispatches that need reasoning; `luna` otherwise. Resolution is in code, not in this file — it lives in the runner's resolver and is printed live by `--print-model-policy`; documents name a site, a tier, and a vendor and never restate a resolved model id. |
| 2026-08-16 | **Bubblewrap is a non-goal; the devcontainer is the isolation boundary.** Codex routes every sandbox mode through bubblewrap, which cannot create a user namespace in this container, so `--sandbox read-only` and `--sandbox workspace-write` both no-op silently: the call exits 0 having read or written nothing. `--sandbox danger-full-access` is the only sandbox value that works here, and every codex arm (single mode's dispatch and the dual-mode codex reviewer arm alike) now uses it. Do not re-open bwrap as a write-prevention mechanism for any codex dispatch. |
| 2026-08-16 | **Write-prevention for reviewer arms moved to the prompt.** With sandboxing removed as a write barrier for the codex arm, `render_reviewer_prompt`'s authority parameter tells dual-mode arms, in both the Task line and the first `Rules:` bullet, that they are read-only and must not create, edit, delete, or move any file; single mode keeps `Apply changes directly`. The claude arm's existing `--disallowedTools Edit,Write,NotebookEdit,Bash` barrier is unchanged and is the harder guarantee of the two. |
| 2026-08-16 | **Every reviewer verdict, `QUESTIONS` included, requires a `READ_PROOF:` line as its first output item.** The runner selects one challenge line per skill from `SKILL.md` before any arm is dispatched, and fails an arm whose final message lacks that line or reproduces it wrong (`read-proof absent` / `read-proof mismatch`), blocking the skill before synthesis. This closes the silent-no-read failure mode a sandboxed-but-broken codex arm could produce: an exit-0 `QUESTIONS` that read nothing. |
| 2026-08-16 | **`agent_skills_pdf.txt` is not given to dispatched reviewers.** The file exists to build the auditing script, not to be read by the agents it dispatches; it stays in the repository at `scripts/auditing/references/agent_skills_pdf.txt` and remains cited as provenance in `SKILL_REVIEW_CHECKLIST.md:11`, `:20`, `:92`. The dispatch prompt in `run_parallel_skill_reviews.sh` no longer names it. |

## Parity register

Blocks that exist in more than one file on purpose. Edit every member in the same change and diff them against each other. Wording drift between members is a defect, not a style difference.

| Family | Members |
| --- | --- |
| Removal authority | `SKILL_REVIEW_CHECKLIST.md` §4 · `SUBAGENT_REVIEW_PROCESS.md` "Removal authority" · `scripts/auditing/reviewer-prompt.md` |
| Verdict enum and status lines | `SKILL_REVIEW_CHECKLIST.md` "Verdicts" · `SUBAGENT_REVIEW_PROCESS.md` "Verdicts" · `scripts/auditing/reviewer-prompt.md` "Output" block · `scripts/auditing/review_log.py` · `synthesis-prompt.md` "Output" |
| Canonical heading families | `SKILL_REVIEW_CHECKLIST.md` §5 · `CANONICAL_HEADINGS` in `scripts/audit_skills.py` — machine-checked by `scripts/check_parity.py` |
| Mechanical check list | `SKILL_REVIEW_CHECKLIST.md` §12 table · the check names emitted by `scripts/audit_skills.py` (`list_check_names()`) — machine-checked by `scripts/check_parity.py` |

**Dropped 2026-08-12: `Skill lifecycle steps`** (`SKILL_REVIEW_CHECKLIST.md` §1 · `.agent/docs/repo-map.md` "Workflow: add a skill"). The member is gitignored, the family name did not match its members, and reviewers are prohibited from editing it — no reviewer or checker could ever verify this row. `.agent/docs/repo-map.md` now carries a one-line pointer back to the checklist instead.

**`Verdict enum and status lines` — read-proof coverage, 2026-08-16.** Every verdict now requires a `READ_PROOF:` line as the reviewer's first output item (see the settled call below). Two of the family's five members carry it as of this change: `SUBAGENT_REVIEW_PROCESS.md` "Verdicts" and the dispatch prompt's Output block in `run_parallel_skill_reviews.sh`. `SKILL_REVIEW_CHECKLIST.md` "Verdicts" and `synthesis-prompt.md` "Output" do not yet, and `scripts/auditing/review_log.py` is deliberately untouched (`READ_PROOF` stays outside `_is_terminator`, by design, so it is never classified). This is a known, flagged gap in the family, not a silent drift — do not close it by editing `SKILL_REVIEW_CHECKLIST.md` or `synthesis-prompt.md` in passing; it is a task of its own.

## Open — awaiting the operator

- **Weak-differentiation skills.** The advisory cluster (`architect-review`, `backend-architect`, `cloud-architect`, `database-architect`, `devops-engineer`, `monitoring-expert`) is expected to return `DIFFERENTIATION: WEAK`. Whether that becomes consolidation, rewrite, or removal is undecided.
- *(nothing — the composition-seam README question was closed 2026-08-11: no.)*

## Deferred — decided, not yet done

The heading and cue lints below are warnings, not issues: 41 of 55 skills carry at least one, and failing the audit on all of them would bury real defects. Each clears during the review pass, not by a mass edit.

- **`heading_variant`** (34 skills) — case, plural, and word-order differences from a canonical family name. Mechanical, one right answer. Promote to an issue once the library is clean.
- **`heading_qualifier`** (34 skills) — a known family carrying a parenthetical. `Workflow (Deterministic)` is vacuous and goes; `Example (Input → Output)` scopes the section and stays. The reviewer rules per heading, which is why this is not auto-corrected.
- **`heading_restated`** (`backend-architect`, `database-architect`, `pdf-files`, `pr-description`, `tracks-conductor-protocol`) — the section's first sentence repeats its own heading. **Measured 2026-08-11** over 55 skills / 539 scored heading pairs against a hand-labelled ground truth: recall within the check's own scope is 3/3, and loosening the threshold adds zero true positives and up to 48 false positives. Do **not** treat this count as a floor — that earlier note was wrong. **Retuned 2026-08-16 (task F):** `##` and `###` headings are both scanned, and backtick spans, markdown links, URLs, bare paths, and filename tokens are stripped before comparison. This closed the one live false positive at `adr-madr-system:116` (matched only on a backticked filename) and surfaced two new true positives from H3 scope (`pdf-files:52`, `pr-description:115`); `adr-madr-system` no longer appears in this row. Remaining gap: step-`Output:` lines are still missed, since only the first prose line under a heading is scored.
- **`activation_cues_in_skill_md`** (`cdd-context`, `performance`, `google-stitch-ai`, `monitoring-expert`, `sre-engineer`) — cues belong in `trigger-cases/`. Flagged, not moved: some cue text may not exist in the trigger-case file yet, and deleting it would lose content.
- **The advisor strategy** for `run_parallel_skill_reviews.sh` — mechanical reviews on a cheap executor, judgment calls escalated. A cost lever, not a correctness fix. Parked.
- **Audit output delta — task D (repo_root_skill_path)**: fixing the unanchored regex and widening `repo_root_skill_path`/`missing_local_refs` to `references/*.md` and `resources/*.md` (one level deep) changed audit output by exactly **+1 ISSUE**: `refactor-clean` now reports `repo_root_skill_path:references/analysis-and-hotspots.md:skills/refactor-clean/scripts/scan_hotspots.sh`, a live false negative closed, not a new defect. Warnings are unchanged: 34 `heading_variant`, 34 `heading_qualifier`, 5 `activation_cues_in_skill_md`, 4 `heading_restated`. No other skill in the library gained or lost an issue or warning. `./scripts/audit-skills.sh` now exits non-zero on this one finding; do not clear it by editing `skills/refactor-clean/references/analysis-and-hotspots.md` — that is the review pass's call, not a tooling fix.

## Trial-gated removal candidates

Content kept only until a run shows it is not needed. Recorded so it is not defended out of habit.
