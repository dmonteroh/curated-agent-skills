# Trigger Cases: database-cost-optimization

## Positive (should activate)
- prompt: "I need help with this: Right-sizing database instances, storage, or connection pools. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Reducing backup/retention costs with clear recovery requirements. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The system is in active incident response. No planning, just implementation."
  expect_activate: no
