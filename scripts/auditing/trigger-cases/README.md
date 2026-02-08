# Trigger Cases

This folder stores activation test cases used by the parallel auditing trigger-test subagents.

## Why this exists

- Keeps activation test prompts out of `skills/*/SKILL.md` to avoid unnecessary prompt token overhead.
- Allows auditing to run behavioral activation tests after skill edits.

## File format

Create one file per skill:

```text
scripts/auditing/trigger-cases/<skill>.md
```

Use this structure:

```md
# Trigger Cases: <skill>

## Positive (should activate)
- prompt: "..."
  expect_activate: yes

## Negative (should not activate)
- prompt: "..."
  expect_activate: no
```

Notes:
- Keep prompts realistic and short.
- Include at least 2 positive and 1 negative case.
- Do not reference these files from `SKILL.md`.
