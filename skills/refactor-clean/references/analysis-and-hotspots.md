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

Treat these as findings to report. Acting on one inside a refactor pass is only safe where the equivalence is obvious on inspection — a set lookup replacing a linear scan, a computation hoisted out of a loop, a string built with a join instead of repeated concatenation. Anything whose equivalence needs a benchmark or a proof is a behavior-risk change and belongs in its own change with its own measurement.

## Keep — What Not to Touch

A smell catalogue with no exceptions over-triggers and eats load-bearing code. Every signal above has a look-alike that must stay.

- **Comments that explain why** — business rules, edge cases, workarounds, ticket links, and explanations of a regex or an algorithm. Remove comments that restate what the code does, never the ones carrying reasons. Test-structure markers (given / when / then) are structure, not noise.
- **Validation and error handling at a system boundary** — user input, external APIs, I/O, nullable persisted fields. A top-level boundary handler that logs and re-raises is deliberate, not a redundant catch.
- **Abstractions that provide a real seam** — testability, more than one implementer, or a boundary the framework requires. A single-implementer interface that buys nothing is indirection; one that makes a dependency swappable in tests is not.
- **Code reached indirectly** — reflection, dynamic dispatch, or string lookup, plus rollback paths held behind a feature flag. A reference count does not see these, so confirm with the owner before treating them as dead.
- **Incidental duplication** — two sites that look alike but serve intents that could diverge. Leave them separate rather than forcing a premature shared abstraction.
- **Complexity that is an established pattern in this codebase, or a deliberate idiom on a hot path.** Follow the convention already in the code before rewriting to a different one.

## Severity Levels

- **Critical**: data loss, security risk, or production outages.
- **High**: maintainability blockers or performance bottlenecks.
- **Medium**: localized code smells and minor inefficiencies.
- **Low**: naming or formatting inconsistencies.

## Hotspot Scan Guidance

- Use `scripts/scan_hotspots.sh` for a quick inventory of large files and TODO/FIXME density.
- If the script is unavailable, prioritize files with the most churn, largest line counts, and highest bug density.
