# Trigger Cases: typescript

## Positive (should activate)
- prompt: "I need help with this: Designing shared types/contracts or public library surfaces. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Fixing hard TypeScript errors, inference issues, or unsafe `any` usage. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: You only need JavaScript guidance. No planning, just implementation."
  expect_activate: no
