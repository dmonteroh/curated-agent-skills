# Provenance

Sources for "Before writing a test" and "When a test you wrote fails" in `SKILL.md`, and for entries 6–12 of `testing-anti-patterns.md`.

- **Sourced from human review of agent-written suites:** every exclusion in "Before writing a test", the project-convention override, the public-surface rule, and the forced-green failure the stop rule targets. The convention-override and private-state wording is carried as the reviewer wrote it.
- **Sourced externally:** the break check, the computed-expected-value and unreachable-assertion shapes (Tom Piaggio, Autonoma AI, "Useless Unit Tests: 5 Patterns That Never Fail"); matcher widening, new skip markers, and fixtures edited into the answer as false-green signatures (Easton, "Codex Test-Driven Development"); never re-blessing a snapshot to match a failure (Brian Austin, DEV Community, "Claude Code for testing"); mocking only at system boundaries and test names that state behavior (localskills team, "Claude Code Unit Tests: Build a Test-Writing Skill"); "flaky" as a conclusion that needs evidence, and test conventions living in the project's own agent docs (P. van Ginkel, "My AI Workflow — Part 8: Test suites for LLM workflows").
- **Not carried:** material on evaluating LLM outputs — synthetic case generation, LLM judges, golden prompt datasets. It tests a model's answers, not code an agent writes tests for.
- **Chosen default:** the three-attempt stop. Reviewers saw forced passes after three to five runs; nothing measured three as the right cut.
