# Deliverables and Handoff (Compact)

Use this when your output needs to be buildable by another agent without follow-up questions.

## Common deliverables

- UI brief (goals/non-goals, flows, acceptance criteria)
- Wireframe-level layout description (not pixel-perfect unless requested)
- Component inventory (what components exist, responsibilities, states)
- Interaction rules (keyboard, focus, confirmation, destructive actions)
- Design system deltas (new tokens, new variants, updated rules)
- QA checklist (light/dark, focus, responsive, empty/error states)

## Component spec template

```md
## <ComponentName>

Purpose:
- ...

Props / inputs:
- ...

States:
- default
- loading
- empty
- error
- disabled

Interaction:
- keyboard: ...
- focus: ...

Visual rules:
- tokens/classes: ...

Acceptance criteria:
- ...
```

## Review output format

When reviewing code, prefer:

- `file:line: issue (why) -> suggested fix`
- group by severity: blocker / should-fix / nice-to-have
- include one verification step per group (how to validate the fix)

