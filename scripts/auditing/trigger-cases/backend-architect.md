# Trigger Cases: backend-architect

## Positive (should activate)
- prompt: "The mobile team wants to start building against an endpoint our team hasn't written yet. How do we run both sides in parallel without them drifting apart?"
  expect_activate: yes

- prompt: "An order touches inventory, payment and shipping. If shipping fails after the card is charged, how should the whole thing unwind?"
  expect_activate: yes

- prompt: "We have a monolithic Node.js orders service that handles checkout, inventory reservation, and invoicing. I want to break it into separate services. Can you propose service boundaries, the API endpoints each should own, how they should communicate (REST vs events), and a rollout plan that avoids downtime?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "We're migrating our legacy payments API to a new service. Help me plan the endpoint versioning, sync vs async communication with the ledger and fraud services, and a phased cutover strategy so we don't take any outage."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Propose how we should partition the new order-processing backend into services and endpoints, including dependencies, contracts, and a safe phased deployment strategy."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Plan a service decomposition for our API platform: ownership of routes, synchronous versus asynchronous service communication, and a backwards-compatible rollout plan."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "how to deploy new api service with zero downtime and talk to other services"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

## Negative (should not activate)
- prompt: "My RabbitMQ consumer keeps redelivering the same message. Which prefetch and retry settings do I set?"
  expect_activate: no

- prompt: "It's two functions in the same module and I'm changing both in one commit — do I really need a formal interface between them?"
  expect_activate: no

- prompt: "Write the SQL migration and ORM changes to add a nullable `deleted_at` column to our orders table and backfill it."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Design the React component hierarchy and state management for our dashboard frontend, and plan how we split it into lazy-loaded bundles."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Draw up a plan for rolling out the new employee onboarding process across our company's offices in phases with no disruption to payroll."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Implement the REST endpoints for our new inventory service, including request validation, database queries, and unit tests."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Split the frontend web application into independently deployable micro-frontends and roll them out without disrupting users."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
