# Trigger Cases: deps-audit

## Positive (should activate)
- prompt: "I need help with this: A repo includes dependency manifests or lockfiles that need a security or license review. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: A release needs a quick dependency risk assessment with actionable next steps. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: No dependency manifests or lockfiles are available. No planning, just implementation."
  expect_activate: no
