# Trigger Cases

This folder stores the activation test cases that `scripts/auditing/skill-eval.py activation` measures. `skill-eval.py cases lint` checks them, and `activation run` refuses a skill whose file has lint errors.

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
  tags: [near-miss]
```

`tags:` is optional. Known tags: `near-miss` (a negative that brushes the skill's topic), `off-register` (a terse, lowercase positive), `generated` and `gen:<vendor>` (written by the isolated generator, and which vendor wrote it), `paraphrase-of:<id>`.

Notes:
- Keep prompts realistic and short.
- Include at least 5 positive and 5 negative cases (the lint floor, a chosen default in `skill_eval/cases.py`), at least one near-miss negative, and one off-register positive.
- Write cases without reading the skill, or generate them with `skill-eval.py judge generate cases`, which never shows the generator the skill. A case written from the skill's own wording measures vocabulary overlap, not intent.
- Do not reference these files from `SKILL.md`.
