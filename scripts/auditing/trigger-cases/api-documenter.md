# Trigger Cases: api-documenter

## Positive (should activate)
- prompt: "I need help with this: The task requires creating or updating API documentation for public or internal users. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: The task requires authoring or refining OpenAPI, AsyncAPI, or GraphQL docs. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is only backend implementation with no documentation work. No planning, just implementation."
  expect_activate: no
