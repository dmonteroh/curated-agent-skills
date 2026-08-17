# Trigger Cases: backend-architect

## Positive (should activate)
- prompt: "I need help with this: Designing a new service/API or changing service boundaries. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Defining contracts (request/response, events, schemas) and compatibility rules. Can you guide me?"
  expect_activate: yes

- prompt: "The mobile team wants to start building against an endpoint our team hasn't written yet. How do we run both sides in parallel without them drifting apart?"
  expect_activate: yes

- prompt: "An order touches inventory, payment and shipping. If shipping fails after the card is charged, how should the whole thing unwind?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: You only need a local code fix with no architectural impact. No planning, just implementation."
  expect_activate: no

- prompt: "My RabbitMQ consumer keeps redelivering the same message. Which prefetch and retry settings do I set?"
  expect_activate: no

- prompt: "It's two functions in the same module and I'm changing both in one commit — do I really need a formal interface between them?"
  expect_activate: no
