# C4 Diagrams (Mermaid)

Mermaid supports C4-style diagrams via a dedicated syntax extension in some renderers (not all platforms enable it). If your target renderer does not support C4, fall back to `flowchart` with explicit boundaries.

## Levels

- Context: system + users + external systems
- Container: apps, data stores, major dependencies
- Component: internals of one container (only if it adds value)

## Guidance

- Keep Context and Container diagrams as the default set.
- Prefer stable names and clear boundaries.
- Show *relationships* and *responsibilities*, not every call.
