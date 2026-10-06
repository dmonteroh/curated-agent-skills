# Trigger Cases: architect-review

## Positive (should activate)
- prompt: "Our domain layer is importing from the HTTP controllers now, and billing has started reading orders' tables directly. Is this as bad as it looks?"
  expect_activate: yes

- prompt: "This aggregate has grown to eleven entities and every transaction locks the whole thing. Is it the right size, or should it be split?"
  expect_activate: yes

- prompt: "Review this microservice design for proper bounded context boundaries"
  expect_activate: yes

- prompt: "Assess the architectural impact of adding event sourcing to our system"
  expect_activate: yes

- prompt: "Evaluate this API design for REST and GraphQL best practices"
  expect_activate: yes

- prompt: "Review our service mesh implementation for security and performance"
  expect_activate: yes

- prompt: "Analyze this database schema for microservices data isolation"
  expect_activate: yes

- prompt: "Assess the architectural trade-offs of serverless vs. containerized deployment"
  expect_activate: yes

- prompt: "Review this event-driven system design for proper decoupling"
  expect_activate: yes

- prompt: "Evaluate our CI/CD pipeline architecture for scalability and security"
  expect_activate: yes

- prompt: "is this microservices setup gonna bite us later look at the repo"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "We’re debating whether to split our billing, catalog, and order workflows into services. Please assess the proposed system structure as a second opinion, including growth limits, coupling risks, and what we’d be giving up."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "My team split our app into 14 microservices six months ago and honestly I think we overdid it. Can you look through the repo layout and the service diagrams in /docs/architecture and tell me if the boundaries make sense and what's going to hurt us as we add more teams?"
  expect_activate: yes
  tags: [generated, gen:claude]

## Negative (should not activate)

- prompt: "Can you refactor the OrderService class so the payment logic is pulled out into its own module? Keep the public method signatures the same and update the tests."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Our API latency spiked after yesterday's deploy. Can you dig through the logs and the recent commits to find what caused it and fix it?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Can you do a code review of this pull request? I want feedback on naming, error handling, and test coverage in the diff."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Explain how the architecture of this repo works so I can onboard. Just walk me through the main components and how a request flows through them, no need to critique it."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Write a migration plan for moving our PostgreSQL database from a single instance to a managed high-availability cluster."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Can you draw a system architecture diagram from this repository and list its components?"
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
