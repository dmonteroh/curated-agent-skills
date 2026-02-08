# Trigger Cases: nodejs

## Positive (should activate)
- prompt: "I need help with this: Building REST APIs, GraphQL backends, or RPC services with Node.js. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Designing backend architecture, middleware, or error handling patterns. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The request is unrelated to Node.js backend development. No planning, just implementation."
  expect_activate: no
