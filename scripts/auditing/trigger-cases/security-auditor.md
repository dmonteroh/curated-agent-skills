# Trigger Cases: security-auditor

## Positive (should activate)
- prompt: "I need help with this: Running security audits or risk assessments. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Reviewing SDLC security controls, CI/CD, or compliance readiness. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: You lack authorization or scope approval for security testing. No planning, just implementation."
  expect_activate: no
