# Trigger Cases: monitoring-expert

## Positive (should activate)
- prompt: "Requirements are unclear and we need help comparing options before implementation."
  expect_activate: yes

- prompt: "Requirements are unclear and we need help comparing options before implementation."
  expect_activate: yes

- prompt: "I want to be paged when a release makes p99 worse than it was right before that deploy, not when it crosses some fixed number."
  expect_activate: yes

- prompt: "We got woken at 3am because an internal mTLS certificate expired. What should we have had in place to see that coming weeks earlier?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The request is only for a single vendor UI walkthrough with no implementation decisions. No planning, just implementation."
  expect_activate: no

- prompt: "After each deploy just curl the health URL a few times and tell me whether the site is up."
  expect_activate: no
