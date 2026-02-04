# Refactor Analysis & Hotspots

Use this reference to identify high-impact refactor targets and gauge severity.

## Code Smell Signals

- Long functions or methods with multiple responsibilities.
- Large classes or modules that mix concerns.
- Duplicate logic across files or layers.
- Deeply nested conditionals or loops.
- Magic numbers or hard-coded configuration.
- Tight coupling between components that makes testing hard.

## SOLID Violation Signals

- Single Responsibility: one unit handles multiple workflows.
- Open/Closed: new behavior requires editing core logic instead of extension.
- Liskov Substitution: subclasses break base assumptions.
- Interface Segregation: consumers depend on methods they do not use.
- Dependency Inversion: concrete dependencies are hard-coded.

## Performance Signals

- Nested loops over large collections.
- Repeated I/O or database calls inside loops.
- Uncached expensive computations.
- Large allocations or repeated object creation.

## Severity Levels

- **Critical**: data loss, security risk, or production outages.
- **High**: maintainability blockers or performance bottlenecks.
- **Medium**: localized code smells and minor inefficiencies.
- **Low**: naming or formatting inconsistencies.

## Hotspot Scan Guidance

- Use `scripts/scan_hotspots.sh` for a quick inventory of large files and TODO/FIXME density.
- If the script is unavailable, prioritize files with the most churn, largest line counts, and highest bug density.
