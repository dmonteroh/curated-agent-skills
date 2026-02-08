# Trigger Cases: cdd-context

## Positive (should activate)
- prompt: "I need help with this: Starting work in a repo and stable context (what/why/how) is needed before making changes. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: A team wants consistent, discoverable context artifacts for humans and agents. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The request is a one-line change and context is already clear. No planning, just implementation."
  expect_activate: no
