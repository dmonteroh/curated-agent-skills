# Trigger Cases: security-auditor

## Positive (should activate)
- prompt: "I need help with this: Running security audits or risk assessments. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Reviewing SDLC security controls, CI/CD, or compliance readiness. Can you guide me?"
  expect_activate: yes

- prompt: "Assume the attacker's goal is reading another tenant's documents. Walk me through every route that gets them there."
  expect_activate: yes

- prompt: "We can fund two of these five hardening items this quarter. Which two shut down the most ways in?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: You lack authorization or scope approval for security testing. No planning, just implementation."
  expect_activate: no

- prompt: "Build me an exhaustive attack tree covering every conceivable threat against the entire platform, no particular objective in mind."
  expect_activate: no
