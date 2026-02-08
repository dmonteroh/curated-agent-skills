# Trigger Cases: deployment-engineer

## Positive (should activate)
- prompt: "I need help with this: Designing or improving CI/CD pipelines and release workflows. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Adding rollout safety (canary/blue-green), automated rollbacks, and runbooks. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: Cloud platform architecture (landing zones, network/IAM design). No planning, just implementation."
  expect_activate: no
