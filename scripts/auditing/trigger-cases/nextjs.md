# Trigger Cases: nextjs

## Positive (should activate)
- prompt: "I need help with this: Building or refactoring React components in a Next.js app. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Working with App Router routing/layouts/loading/error boundaries. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The project is a plain React SPA or component library. No planning, just implementation."
  expect_activate: no
