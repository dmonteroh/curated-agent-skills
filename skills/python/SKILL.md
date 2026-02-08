---
name: python
description: "Build modern Python 3.x services and libraries with async patterns, robust typing, and production-ready practices. Use for Python implementation, refactors, and tooling guidance when a Python runtime is required."
category: language
---
# Python Implementation

Provides guidance for modern Python development with a focus on correctness, performance, and maintainability.

## Use this skill when

- Building or refactoring Python 3.x services, CLIs, or libraries
- Designing async workflows or concurrency patterns
- Setting up Python tooling, linting, or testing workflows

### Activation cues

- "Implement this in Python"
- "Add async/await" or "use asyncio"
- "Set up pytest/ruff/mypy"
- "Build a FastAPI/Django endpoint"

## Do not use this skill when

- The task is primarily about another runtime or language
- The request is strictly about data science notebooks or ML training pipelines

## Inputs to confirm

- Target Python version and runtime constraints
- Packaging expectations (`pyproject.toml`, `uv`, `pip`, or `poetry`)
- Dependency constraints (allowed third-party packages or stdlib-only)
- Execution model (sync vs async, web framework or standalone)
- Quality gates (tests, lint, type checking)

## Workflow (Deterministic)

1. Clarify scope and constraints.
   - Output: confirmed runtime, packaging, and acceptance criteria.
2. Choose architecture and libraries.
   - Decision: If the project already mandates a framework, follow it; otherwise keep dependencies minimal and prefer the standard library when possible.
   - Decision: If third-party dependencies are restricted, keep to stdlib and lightweight patterns.
   - Decision: If a web API is needed, pick FastAPI or Django; if CLI/script, use standard library + `argparse` or approved CLI helpers.
   - Output: selected stack and module boundaries.
3. Choose concurrency model.
   - Decision: If I/O-bound or high concurrency, use `async`/`await`; otherwise stay synchronous.
   - Output: sync/async approach and key primitives.
4. Implement with types and validation.
   - Output: typed interfaces, input validation at boundaries, and clear error handling.
5. Add tests and tooling guidance.
   - Output: test plan or tests added plus lint/type-check notes.
6. Summarize changes and verification.
   - Output: concise change summary and commands (if any) to validate.

## Common pitfalls to avoid

- Mixing sync and async without clear boundaries
- Skipping input validation at API/CLI boundaries
- Adding heavy dependencies when the stdlib is enough
- Ignoring project dependency constraints
- Providing unbounded concurrency or missing timeouts
- Assuming dependencies or tooling are already available

## Examples

**Example input**: "Add a FastAPI endpoint that accepts JSON and validates fields."

**Expected output**: A FastAPI route with Pydantic models, validation errors handled, and a note on running `pytest` and `ruff` if available.

**Example input**: "Convert this blocking HTTP loop to async." 

**Expected output**: Use `httpx.AsyncClient` if approved, async entrypoint, and note any required event loop changes.

## Output Contract (Always)

Report using this format:

- Summary: 1–3 bullets describing what changed
- Files changed: list of paths updated or created
- Tests/verification: commands run or suggested (state if not run)
- Follow-ups: questions or next steps if anything is blocked

## References (Optional)

- Reference index: `references/README.md`
