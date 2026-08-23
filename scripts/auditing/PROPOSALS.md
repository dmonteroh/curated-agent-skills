# Removal proposals — pending rulings

<!-- Machine-managed by scripts/auditing/proposals.py. `record` (run by
run_parallel_skill_reviews.sh after a review pass) appends one entry per
proposal from the synthesis .removals artifacts; `apply` executes rulings and
moves resolved entries to the rulings record at logs/removal-rulings.md, so
this file holds only proposals still awaiting a ruling and ends after this
comment when nothing awaits one.

Operator: edit ONLY an entry's `ruling:` line — pending | approved |
declined, optionally followed by " — <note>". Then run:
  .venv/bin/python scripts/auditing/proposals.py apply
Any other edit fails the checksum lint and blocks apply until restored.

Dedupe is by content hash (the id in each entry heading), so a re-worded
duplicate of an already-ruled proposal can reappear here; under Quality
Gate 7 that is a review defect — decline it and the ruling is permanent. -->

## proposal bc26a53d3a02 — prompt-engineering

- recorded: 2026-08-22
- ruling: approved
- checksum: 85439b32f0b78a81

```text
`skills/prompt-engineering/SKILL.md`, `## Reporting format` (lines 169-178), whole section. Checklist section 4, One Rule One Home, at whole-section granularity, which stays propose-never-execute. Evidence, verified against the file: five of its six numbered items restate `## Output contract` (:159-167) field for field — "Prompt (copy/paste)" restates the Prompt block bullet (:163), "Assumptions" (:164), "Open questions" (:165), "Evaluation plan" (:166) and "Next actions" (:167) each restate their identically named bullet. Its own lead sentence, "Use this exact structure in the response:", adds only a fixed presentation order over content the Output contract already fixes. Both reviews proposed this section independently, and the identical pattern is ruled Approved and executed in OPEN_ITEMS.md "Removal rulings" for ten other skills — `cli-tools`, `cloud-architect`, `database-migration-orm`, `gdpr-data-handling`, `google-stitch-ai`, `mermaid-expert`, `secrets-management`, `security-auditor`, `tutorial-engineer`, and `testing`. What would be lost: the fixed 1-6 response ordering, and the standalone "Summary" item, which is the one element with no Output contract counterpart. Both are foldable into `## Output contract` with no information loss by adding an ordering clause and a Summary bullet to that section; several of the ten prior rulings resolved the same residue that way. Approving as written without that fold drops the opening one-line summary from the skill's stated output. The section is 45 cl100k_base tokens (measured 2026-08-22).
```
