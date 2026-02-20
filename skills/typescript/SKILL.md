---
name: typescript
description: "Provides TypeScript architecture and typing guidance for strictness/tsconfig decisions, advanced type design, fixing type errors, type-checking performance, and boundary runtime validation; use when resolving TypeScript typing or configuration issues."
metadata:
  category: language
---
# TypeScript Skill

Provides a deterministic workflow for TypeScript architecture, day-to-day implementation, and advanced types.

## Use this skill when

- Designing shared types/contracts or public library surfaces
- Fixing hard TypeScript errors, inference issues, or unsafe `any` usage
- Deciding `tsconfig` strictness and an incremental migration strategy
- Improving type-checking performance (slow `tsc`, editor lag)

## Do not use this skill when

- You only need JavaScript guidance
- You need UI/UX design rather than type design

## Required inputs

- Relevant TypeScript snippets, error messages, and expected behavior
- Project constraints (runtime boundary vs internal logic)
- Current `tsconfig.json` (if config changes are needed)

## Workflow (Deterministic)

1. Scope the surface area (boundary vs internal).
   - Output: a short list of boundary inputs and internal invariants.
2. Decide validation strategy.
   - If boundary data is untrusted, plan runtime validation and narrow from `unknown`.
   - If data is internal, skip runtime validation and focus on static types.
   - Output: validation plan and narrowing approach.
3. Model invariants with types.
   - Prefer discriminated unions, branded types, or mapped types as needed.
   - Output: proposed type definitions with invariant notes.
4. Apply fixes and guardrails.
   - If migration is required, propose incremental steps (file-by-file or package-by-package).
   - Output: concrete code changes or refactor steps, avoiding new `any` and `@ts-ignore`.
5. Verify and report.
   - Output: suggested verification commands, expected outcomes, and any remaining risks.

## Common pitfalls to avoid

- Widening types by defaulting to `any` or `unknown` without narrowing
- Using `@ts-ignore` when a type-safe refactor is possible
- Exporting overly generic public types that leak implementation details
- Adding strictness flags without a migration plan

## Output contract

Provide results in this format every time:

1. Summary: 1–3 bullets describing the change.
2. Types/Code: updated type definitions or code fixes.
3. Config/Migration: `tsconfig` adjustments and rollout steps (or “None”).
4. Verification: commands run or to run (with expected outcomes).
5. Risks/Follow-ups: remaining concerns or next steps (or “None”).

## Examples

**Input**
"We ingest webhook JSON and keep getting `unknown` errors. Can you model the payload and validate it?"

**Expected output (sketch)**
1. Summary: Added `WebhookPayload` discriminated union and runtime parsing.
2. Types/Code: `type WebhookPayload = ...`; `parseWebhookPayload(...)` using runtime guards.
3. Config/Migration: None.
4. Verification: `tsc --noEmit` (no errors), unit test for invalid payload.
5. Risks/Follow-ups: None.

## Scripts (Optional)

- Read-only scan: `scripts/ts_doctor.sh <repo-root>`
  - Requirements: `rg` (preferred) or `grep`.
  - Verification: confirm output lists risky patterns and suggested commands.

## References (Optional)

- Index: `references/README.md`
- Implementation playbook: `references/implementation-playbook.md`
