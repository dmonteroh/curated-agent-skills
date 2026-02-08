# Trigger Cases: nestjs

## Positive (should activate)
- prompt: "I need help with this: Creating or refactoring a NestJS service (modules/providers/controllers). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Designing request lifecycle behavior (auth, validation, logging, errors). Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The service is not NestJS (use the stack-specific skill instead). No planning, just implementation."
  expect_activate: no
