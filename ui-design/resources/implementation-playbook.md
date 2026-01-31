# UI Design - Implementation Playbook (Design + Spec)

Use this when you need a repeatable sequence to turn ambiguous requirements into something buildable.

## Inputs

- Feature request (1-3 sentences).
- Users/roles and what they can/can't do.
- Data constraints (latency, offline, pagination, errors).
- Existing design system rules (if any).

## Default Loop

1) Write the brief
- Goals / non-goals.
- Success criteria (what a reviewer can verify).
- Primary flow + at least one failure flow.

2) Map states (required)
- Loading, empty, error, disabled, permission denied.
- Define the error copy style and where errors appear (inline vs toast vs banner).

3) Define component responsibilities
- Small number of components with clear boundaries.
- Each component: inputs, outputs, and state ownership.

4) Apply design system rules (if present)
- Prefer semantic tokens when they exist.
- If no design system exists, propose a *minimal* token set and surface stack.

5) A11y + interaction pass
- Keyboard navigation + focus management.
- Labels, hit targets, contrast, reduced motion.

6) Review contract
- If reviewing code, produce `file:line` findings and a prioritized fix list.

## Anti-patterns

- “Looks good” without defining states and success criteria.
- Hardcoding palette usage everywhere when semantic tokens exist.
- Shipping interactive elements without keyboard support or focus visibility.
- Mixing “status colors” and “categorical colors” without a hierarchy.

