# Trigger Cases: react

## Positive (should activate)
- prompt: "I need help with this: Building/refactoring React components (hooks, composition). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Choosing state management (local state, context, Zustand/Redux, query caching). Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The project uses Next.js App Router or React Server Components. No planning, just implementation."
  expect_activate: no
