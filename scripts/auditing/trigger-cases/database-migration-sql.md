# Trigger Cases: database-migration-sql

## Positive (should activate)
- prompt: "I need help with this: The task involves writing or operating versioned `.sql` migration files. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: The change needs expand/contract patterns for backwards compatibility. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The workflow is ORM-managed migrations rather than raw SQL files. No planning, just implementation."
  expect_activate: no
