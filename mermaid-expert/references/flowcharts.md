# Flowcharts

## Tips

- Prefer `flowchart LR` (left-to-right) for pipelines; `TB` for hierarchies.
- Keep node IDs short; use labels to display text.
- Use subgraphs to group components by boundary (service, network zone, team).

## Common Shapes

- `([Start])` / `([End])` for terminals
- `{Decision?}` for branching
- `[(DB)]` for persistence
- `[Process]` for steps

## Patterns

- Use one decision per branch cluster.
- Prefer explicit edge labels (`-->|Yes|`).
- Avoid spaghetti: split into multiple diagrams if needed.
