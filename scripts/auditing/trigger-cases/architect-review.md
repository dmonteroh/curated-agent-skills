# Trigger Cases: architect-review

## Positive (should activate)
- prompt: "I need help with this: Reviewing system architecture or major design changes. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Evaluating scalability, resilience, or maintainability impacts. Can you guide me?"
  expect_activate: yes

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

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is a small code review without architectural impact. No planning, just implementation."
  expect_activate: no
