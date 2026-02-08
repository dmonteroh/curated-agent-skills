# Trigger Cases: tailwind

## Positive (should activate)
- prompt: "I need help with this: Defining a Tailwind-driven design system (tokens, color semantics, typography, spacing). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Standardizing component patterns (variants/sizes/states) across a codebase. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is only selecting a frontend framework or component library. No planning, just implementation."
  expect_activate: no
