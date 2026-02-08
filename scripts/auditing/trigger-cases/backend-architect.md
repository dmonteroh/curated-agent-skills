# Trigger Cases: backend-architect

## Positive (should activate)
- prompt: "I need help with this: Designing a new service/API or changing service boundaries. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Defining contracts (request/response, events, schemas) and compatibility rules. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: You only need a local code fix with no architectural impact. No planning, just implementation."
  expect_activate: no
