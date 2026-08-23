# Advanced Features

Use these when they increase clarity; avoid them if they reduce render portability.

## Config Frontmatter

- Set theme variables (fonts, colors) for readability.
- Keep styling minimal; content is the priority.

## Links And Clicks

Some renderers support linking nodes to URLs.

## Subgraphs As Boundaries

Use subgraphs to show:

- Trust boundaries
- Network zones
- Ownership boundaries
- Deployment units

## Large Diagrams

- Split by domain/bounded context.
- Provide a "map" diagram that links to detailed diagrams.
- Split once the main story stops reading without tracing edges by hand, unless the diagram is deliberately a map. Published node-count cut-offs are chosen defaults with no measurement behind them and they disagree: this reference has long used ~30-50 nodes as the ceiling, while other guidance treats 5-15 as the comfortable range. Neither figure is derived from the other, so use either only as a prompt to re-check readability, never as a threshold to pass.
