---
name: subagent-driven-development
description: Use when executing an implementation plan by delegating independent tasks to fresh subagents (implementer + reviewers) with deterministic task packets and verification gates. Works with non-interactive subagents (Codex exec) and interactive environments.
---

# Subagent-Driven Development

Use subagents to execute a plan with high throughput and low context thrash.

Core principle: **fresh implementer per task + strict review gates + evidence before completion**.

## Use this skill when

- You have 2+ reasonably independent tasks (or task phases) to execute
- You can define scope boundaries per task (paths/modules)
- You want deterministic outputs per task (changes + verification)

## Do not use this skill when

- The work is tightly coupled and requires constant cross-task coordination
- The requirements are still unclear (brainstorm first)

## Workflow (Deterministic)

### 0) Prepare (controller)

- Read the plan/spec once.
- If the work is not already partitioned, first use `dispatching-parallel-agents` to partition by domain and define scope boundaries.
- Partition into tasks with explicit:
  - scope (allowed paths)
  - acceptance criteria
  - verification command(s)
- Decide execution mode:
  - Sequential subagents (default; lowest risk)
  - Parallel subagents (only if file overlap is unlikely)

### 1) Implement (per task)

- Dispatch an implementer subagent with a complete **task packet**.
- Non-interactive environments: the implementer must STOP and return QUESTIONS if anything is ambiguous.

### 2) Verify (controller gate)

- Do not claim completion without fresh verification evidence.
- Run the task’s verification commands (or explicitly state why you can’t).

### 3) Review gates (per task)

- Spec compliance reviewer: verifies “nothing missing, nothing extra”.
- Code quality reviewer: checks correctness, maintainability, tests, safety.
- If a reviewer fails: dispatch the implementer again with a narrowed fix packet.

### 4) Integrate

- Merge results carefully if multiple tasks ran in parallel.
- Re-run full-suite verification before finishing.

## Output Contract (Always)

- A task partition plan (tasks + scope + verification).
- For each task:
  - implementer summary (root cause, changes, files)
  - verification evidence (commands + results)
  - spec compliance verdict
  - code quality verdict
- Final integration verification summary.

## Bundled Prompts

- `implementer-prompt.md`
- `spec-reviewer-prompt.md`
- `code-quality-reviewer-prompt.md`

## References (Optional)

- Codex subagents via `codex exec`: `references/codex-exec.md`
- Task packet template: `references/task-packet-template.md`
- Review packet template: `references/review-packet-template.md`

## Notes

- This skill is standalone.
- If you also have a parallelization skill available, its partitioning heuristics can help, but do not require it.
