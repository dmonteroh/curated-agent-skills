# Trigger Cases: deployment-engineer

## Positive (should activate)
- prompt: "I need help with this: Designing or improving CI/CD pipelines and release workflows. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Adding rollout safety (canary/blue-green), automated rollbacks, and runbooks. Can you guide me?"
  expect_activate: yes

- prompt: "Our release sat waiting nine hours last night: the approver was on holiday and the canary metric never reported either way. What should a gate do when its signal just never arrives?"
  expect_activate: yes

- prompt: "We're dropping a column next release. How do I stage that so we can still roll the app back if the deploy goes bad?"
  expect_activate: yes

- prompt: "Our pipeline minifies and repacks the bundle after the tests pass. The upload succeeded and the artifact loads fine, but the page came up blank in prod. How do we gate that step so it can't happen again?"
  expect_activate: yes

- prompt: "We compress the model before it goes to the inference server, so the output is never byte-identical to what we tested. What is the release supposed to compare?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: Cloud platform architecture (landing zones, network/IAM design). No planning, just implementation."
  expect_activate: no

- prompt: "Should we serve these images as WebP or AVIF, and what quality setting gets us under 200KB?"
  expect_activate: no

- prompt: "Help me decide whether this should be one table or three, and which columns need indexes."
  expect_activate: no
