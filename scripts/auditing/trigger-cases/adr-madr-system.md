# Trigger Cases: adr-madr-system

## Positive (should activate)
- prompt: "I need help with this: Making a decision that affects architecture boundaries, persistence, auth/security posture, API style, reliability/SLOs, scaling, or major vendor/tool choices. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Changing a previously accepted architectural decision (create a new ADR that supersedes the old one). Can you guide me?"
  expect_activate: yes

- prompt: "While wiring up the queue we quietly settled on SQS over Kafka in a Slack thread. Nobody asked for paperwork, but in six months nobody will remember why."
  expect_activate: yes

- prompt: "Reading back over what we just built, I realise we committed to token auth for the whole platform without ever discussing it as a decision."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: Capturing minor implementation notes, routine refactors, or small patches with no architectural impact. No planning, just implementation."
  expect_activate: no
