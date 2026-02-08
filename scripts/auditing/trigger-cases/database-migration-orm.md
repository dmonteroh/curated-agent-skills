# Trigger Cases: database-migration-orm

## Positive (should activate)
- prompt: "I need help with this: Creating or reviewing ORM migrations (schema + data transforms). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Planning safe, staged rollouts (expand/contract) with backfills. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The project uses forward-only SQL migration files as the primary mechanism. No planning, just implementation."
  expect_activate: no
