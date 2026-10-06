# Trigger Cases: api-documenter

## Positive (should activate)

- prompt: "Our REST API for the billing service has barely any docs. Can you go through the Express routes in src/routes/ and write reference documentation for every endpoint, including request/response schemas and curl examples that actually work?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I need an OpenAPI 3.1 spec written for our FastAPI app's public endpoints, with accurate parameter descriptions, request bodies, response schemas, and example payloads that I can publish as developer docs."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Review the existing reference docs for our webhooks API and fix whatever is wrong: incorrect paths, missing required fields, example JSON that wouldn't validate against the real schema. Make the examples runnable."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "docs for our rest api are wrong fix them"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Audit and correct the API reference for the Payments service: fix outdated paths and parameters, document error responses, and add working JavaScript and Python examples."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Write OpenAPI-based developer docs for the new v2 endpoints so integrators have accurate methods, payload fields, response models, and sample requests."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Document the webhook API reference, including subscription endpoints, event payload schemas, signature verification headers, and end-to-end examples."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Add a new DELETE /api/users/:id endpoint to our Express app with validation and unit tests."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Add JSDoc comments to the internal helper functions in src/utils/ explaining what each parameter does."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Generate a Postman collection and load test script that hits every endpoint in our API to check response times under traffic."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Implement the missing v2 API endpoints and add integration tests for their request validation and error handling."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Analyze our API access logs and recommend changes to reduce latency and 5xx errors."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Document our internal deployment process for releasing API services to production."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
