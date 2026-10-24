# Trigger Cases: adr-madr-system

## Positive (should activate)
- prompt: "While wiring up the queue we quietly settled on SQS over Kafka in a Slack thread. Nobody asked for paperwork, but in six months nobody will remember why."
  expect_activate: yes

- prompt: "Reading back over what we just built, I realise we committed to token auth for the whole platform without ever discussing it as a decision."
  expect_activate: yes

- prompt: "Please create a new architecture decision record for our switch from REST to gRPC for internal service communication. Mention that we also considered GraphQL and plain REST with OpenAPI, and the reasons we rejected them."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "ADR 0007 says we use Redis for session storage, but we moved to signed JWTs last sprint. Write a new ADR that supersedes 0007 and mark the old one as superseded."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Add a numbered architecture decision record under docs/adr for adopting OpenTelemetry, with the options we considered and the trade-offs behind the final choice."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Record the decision to standardize on Terraform for infrastructure provisioning in a new numbered decision file, comparing Pulumi and CloudFormation."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "write an adr for postgres over mysql and dynamodb"
  expect_activate: yes
  tags: [generated, off-register, gen:codex]

## Negative (should not activate)

- prompt: "Can you write a design doc proposing how we should structure the new notification system? Include the architecture, data flow, and open questions, since we haven't decided anything yet."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Write a README section explaining how to set up the dev environment and run the test suite."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Add a code comment above the retry logic in client.py explaining why we chose exponential backoff."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Write a postmortem for yesterday's database outage, including timeline, root cause, and action items."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Add a changelog entry noting that the API now uses GraphQL."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Create a runbook for diagnosing Redis cache failures in production."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Implement the database migration from MySQL to PostgreSQL and add tests."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
