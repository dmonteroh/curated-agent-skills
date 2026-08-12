# Skill Review Checklist

Binding quality bar for every skill under `skills/`. `scripts/audit_skills.py` enforces the mechanical items; a reviewer enforces the rest. On conflict, this file wins over any other guidance, including the vendored resources.

**North star: predictability of process.** A skill's job is to make the process an agent follows repeatable — not to make its output identical, and not to be complete. Judge every sentence against that.

Depth and worked examples live in `references/authoring-guidance.md`. Calls already settled — which a review must not re-open — live in `OPEN_ITEMS.md`. Read both before ruling on a judgment call.

## Provenance of this bar

- `resources/agent_skills_pdf.txt` — text extract of Rick Hightower, "Agent Skills: The Universal Standard Transforming How AI Agents Work", Medium, Jan 2026 (printed 2026-02-04), alongside the vendor docs listed in `README.md`. Background only; this file wins on conflict.
- `mattpocock/skills` → `writing-great-skills` (MIT). Patterns reimplemented in this repo's words, never copied: the process-predictability north star, leading words, teach-by-contrast, the no-op test.
- The operator's `ai-workflows` → `workflows/conventions.md`: One Rule One Home, the parity register, open items, trial-gated removal.
- The `dot-agent` operating model's skill doctrine: verification claims must be falsifiable, not asserted.

## 1. Discovery contract — mandatory

- Frontmatter carries `name`, `description`, and `metadata.category`, and no other top-level key.
- `name` equals the folder name, lowercase with hyphens.
- `description` states what the skill does *and* when to use it, in third person, within the frontmatter token budget.
- Activation cues live in `scripts/auditing/trigger-cases/<skill>.md`, never in `SKILL.md`.

## 2. Boundary — mandatory

- A `Use this skill when` section.
- A `Do not use this skill when` section. This is the highest-signal section in the file: a skill that never says when to stand down will fire when it should not.

## 3. Differentiation — reported, never acted on

Does this skill change what a frontier model would do unprompted? It earns its maintenance cost only if it carries at least one of: an opinionated house convention the model would not default to, a non-obvious process with real decision points, embedded tooling that makes behavior deterministic, or a correction for something models reliably get wrong.

Report `DIFFERENTIATION: STRONG` or `DIFFERENTIATION: WEAK` with one line of evidence. **A WEAK verdict is a flag for the operator, not a licence to delete or rewrite.** Whether a weak skill is repaired, replaced, or removed is the operator's call alone.

## 4. Subtraction — mandatory

Every review runs a pruning pass and reports its result, including "nothing to cut".

Delete without asking:

- a sentence that restates its own heading;
- a restatement of the frontmatter description;
- a second statement of a rule already stated elsewhere in the same file (One Rule, One Home);
- a vacuous heading qualifier — `(Deterministic)`, `(Always)`, `(best results)`;
- a workflow step whose only output is "report per the output contract".

Propose, never execute: removing a whole section, a file under `references/` or `scripts/`, or the skill itself. A proposal carries the evidence and what would be lost; the operator rules on it.

**Adding is not the goal.** A review that removes forty lines and adds none is a successful review. So is one that changes nothing.

## 5. Structure — earned, not mandatory

Beyond §1 and §2, shape follows the job. A skill with one procedure gets one procedure; a skill guarding six failure modes gets a section per failure mode. Never add a section because other skills have one.

When a section from a known family is present, use its canonical heading: `Workflow`, `Output contract`, `Required inputs`, `Common pitfalls`, `Decision points`, `Constraints`, `Examples`, `References`, `Scripts`. Wording variants are lint, not voice.

## 6. Voice

- Third person for the frontmatter `description` and the skill's opening framing: "Provides…", "Produces…", "Use this skill to…".
- Imperative for procedure steps: "Capture the constraints", "Stop and report". Imperative steers behavior; the third-person framing keeps the file a tool rather than an identity.
- No personas, no "You are…", no voice shift inside `references/`.
- Naming a concept its author owns — "a seam, in Feathers' sense" — is a leading word, not a persona.

## 7. Instructions

- Steps produce real outputs: an artifact, a decision, a command run. Not "report this".
- Decision points are explicit: if X, do Y.
- Where the skill exists to prevent a default failure, encode a stop that can fail, not an advisory line.
- Verification claims are falsifiable: name the check and what its failure looks like. "Confirm the change works" is not a check.
- Do not over-constrain. A rule that overrides judgment a frontier model exercises better unaltered is a cost, not a control: constrain the process, leave the craft.
- No time-sensitive facts unless labelled as such.

## 8. Examples and output

- At least one concrete example or input/output pair. Prefer contrast — the wrong version beside the right one — wherever the failure is easy to fall into.
- An output contract only where the skill's product is a report. It states what the consumer receives, not what the agent feels obliged to mention.

## 9. Scripts and references

- References are local to the skill and one level deep.
- Script paths are written skill-relative — `scripts/x.sh` — never repo-root style. A repo-root path does not resolve once the skill is installed to `~/.codex/skills/<name>/`.
- Scripts state usage, required packages, and how to verify their output.
- No network assumptions.
- Route material into `references/` when a reader does not need it in line — not because a token count was crossed. Add `references/README.md` as an index at two or more files.

## 10. Size

- `SKILL.md` stays under ~5000 tokens; warning at 4500.
- Length beyond 200 lines is a warning, not a defect. The job sets the length.

## 11. Independence — mandatory

- A skill never requires another skill to be installed and never checks for one. Cross-skill sequencing belongs in the consuming project's `AGENTS.md`.
- A skill may mention partitioning or parallel work only where it stays self-contained.
- Patterns this library rejects on purpose — routers, cross-skill `/name` invocation, shared setup skills, hard dependencies, plugin-only distribution — and the reasoning: `references/authoring-guidance.md`.

## Verdicts

Exactly one status line ends a review:

- `REVIEW_STATUS: NO-CHANGE` — the skill meets the bar. A first-class outcome.
- `REVIEW_STATUS: CHANGED` — edits applied.
- `QUESTIONS` — blocked on ambiguity. Do not guess.

Alongside it, always: the `DIFFERENTIATION:` line from §3 and a `REMOVAL PROPOSALS:` block from §4, written as `none` when there are none.
