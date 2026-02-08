# Trigger Cases: secrets-management

## Positive (should activate)
- prompt: "I need help with this: Handling credentials, signing keys, API keys, TLS material, or connection strings. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Designing secret retrieval for CI/CD or runtime workloads. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: You only need local dev values that will never be shared (use `.env` locally, never commit). No planning, just implementation."
  expect_activate: no
