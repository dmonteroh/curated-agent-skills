# Codex Subagents via `codex exec`

This reference captures a reliable pattern for spawning a separate, non-interactive Codex agent process.

## Key properties

- Subagents are **non-interactive**: no mid-task back-and-forth.
- Subagents can read local skills/files **from disk** (within sandbox limits).
- Subagents do not share chat context; include all needed context in the prompt or point them to files to read.

## Sandboxing

The sandbox you pass applies to that subagent only:

- `read-only`: can read files but cannot edit/move/write.
- `workspace-write`: can write inside the workspace.
- `danger-full-access`: unrestricted; use only with explicit intent.

## Best-practice prompt template

```sh
codex exec --sandbox workspace-write "
Task: <one sentence, explicit outcome>.
Scope: Only touch <paths>. Do not touch <paths>.
Rules:
- Preserve filenames and content unless explicitly told to edit.
- If a rule conflicts or requirements are ambiguous, STOP and output QUESTIONS (do not guess).
Steps:
1) Inspect <files> to establish current state.
2) Perform <exact actions>.
3) Update <specific file(s)> with <specific changes>.
Output:
- List files changed.
- List files moved.
- Summarize edits with file paths.
- Verification performed (commands + result), or explain why verification could not be run.
"
```

## Practical tips

- Prefer `workspace-write` by default.
- If the task is risky, restrict scope to a small directory and explicit file list.
- Require explicit reporting: files changed + verification.
