# Removal proposals — pending rulings

<!-- Machine-managed by scripts/auditing/proposals.py. `record` (run by
run_parallel_skill_reviews.sh after a review pass) appends one entry per
proposal from the synthesis .removals artifacts; `apply` executes rulings and
moves resolved entries to OPEN_ITEMS.md "Removal rulings", so this file holds
only proposals still awaiting a ruling and ends after this comment when
nothing awaits one.

Operator: edit ONLY an entry's `ruling:` line — pending | approved |
declined, optionally followed by " — <note>". Then run:
  .venv/bin/python scripts/auditing/proposals.py apply
Any other edit fails the checksum lint and blocks apply until restored.

Dedupe is by content hash (the id in each entry heading), so a re-worded
duplicate of an already-ruled proposal can reappear here; under Quality
Gate 7 that is a review defect — decline it and the ruling is permanent. -->

## proposal b38ae4eb4733 — brand-voice

- recorded: 2026-08-18
- ruling: approved
- checksum: 17fe3a86d781c17f

```text
skills/brand-voice/SKILL.md, "Provenance" (:139-141): consider removing the section. Evidence: explains rewrite history rather than the operational procedure; removal loses the rationale for dropping named-person defaults and the meaning of *(Authored)* annotations.
```

## proposal df95bb728a9f — cli-tools

- recorded: 2026-08-18
- ruling: approved
- checksum: d333482883147760

```text
skills/cli-tools/SKILL.md, ## Reporting format (whole section, :122-133) — Evidence: restates ## Output contract (:84-89) field-for-field (Command/flag matrix / Output behavior and exit codes / Validation rules / Test plan vs. the same four items), and its Notes half restates ## Common pitfalls and ## Decision points, both of which already stand as their own sections. Grounded in §4 (a second statement of a rule already stated elsewhere in the same file), but whole-section removal stays propose-never-execute per §4. What would be lost: nothing — every field is already stated once, in its owning section.
```

## proposal bf3b7fd145ef — cloud-architect

- recorded: 2026-08-18
- ruling: approved
- checksum: 98c3d8390ce09bc3

```text
SKILL.md:82-90, ## Reporting format - restates ## Output contract (SKILL.md:73-80) field-for-field: same six items, reworded. Section 4 (One Rule, One Home: "a second statement of a rule already stated elsewhere in the same file"); whole-section removal stays propose-never-execute. What would be lost: nothing - every field already lives in Output contract.
```

## proposal 4073fea16a7f — code-review

- recorded: 2026-08-18
- ruling: approved
- checksum: 0ee35d3a69c5ba0a

```text
references/pitfalls-and-practices.md (section 4). Evidence: never linked from SKILL.md's body; its lists overlap the renamed Common pitfalls section and the mode checklists. Loss: an unreachable duplicate list.
```

## proposal 3acbf2d5177e — interruption-budget

- recorded: 2026-08-18
- ruling: approved
- checksum: 265f32f3a34059a3

```text
`skills/interruption-budget/SKILL.md`, section `## Rationing the remainder — a design pattern, not established practice` (lines 99-109), plus its `references/rationing-pattern.md` pointer in `## References` (SKILL.md:146) and the `references/rationing-pattern.md` file itself. Evidence: the section's own source is disclaimed *not yet implemented* — no ranking, state store, auto-accept list, or reopen command was ever built (SKILL.md:11; references/rationing-pattern.md:3) — yet it is the practice the skill is named for; it instructs nothing an agent can execute today ("carry the three factors as ranking inputs; carry no combining rule and no constants," SKILL.md:105), which the checklist's North star ("a skill's job is to make the process an agent follows repeatable") does not credit. What would be lost: the honest gap-analysis and provenance trail that could seed a real implementation, and the explicit disclaimer (SKILL.md:11) that currently blocks anyone from citing a budget mechanism that doesn't exist. Stays propose-only under checklist section 4 ("Propose, never execute: removing a whole section ... or a file under references/").
```

## proposal 9c4325f3cfa0 — mcp-server-development

- recorded: 2026-08-18
- ruling: approved
- checksum: ce075c215041356a

```text
`SKILL.md:92-97`, `## Reporting format` — whole section. Evidence (converging from both reviews): for a non-report-producing skill §8 does not license a reporting-format section either; separately, three of its four bullets restate `## Output contract` in closer format detail (Tools/Examples/Evals), leaving only the `Summary: 3-6 bullets` bullet novel. What would be lost: the prescribed presentation format outright, or — if that Summary bullet is folded into `## Output contract` first — nothing.
```

## proposal b4f335784960 — network-change-review

- recorded: 2026-08-18
- ruling: approved
- checksum: d3e37b52abc639c6

```text
skills/network-change-review/SKILL.md, ## Common pitfalls (section 4) - Evidence: five of six bullets restate a rule already stated once elsewhere in SKILL.md (diff-against-device/template-is-not-baseline restates Workflow step 7 twice over; persist-only-after-checks restates Workflow step 9; subnet-vs-wildcard-mask restates the Decision points bullet; ACL-direction restates the ACL placement review's first question); the sixth bullet (SNMPv2 community strings) is not restated elsewhere in SKILL.md. What would be lost: a single skimmable negative-summary list, and the one item (SNMPv2 string) that carries content not stated elsewhere in SKILL.md. Whole-section cut stays propose-never-execute per section 4.
```
