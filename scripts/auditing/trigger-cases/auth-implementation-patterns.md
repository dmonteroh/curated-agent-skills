# Trigger Cases: auth-implementation-patterns

## Positive (should activate)
- prompt: "I need help with this: Implementing user authentication systems. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Securing REST or GraphQL APIs. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Exposing a local, already-trusted capability (an agent daemon, dev tool, or CLI) to a remote or third-party caller. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: Only UI copy or login page styling is needed. No planning, just implementation."
  expect_activate: no
