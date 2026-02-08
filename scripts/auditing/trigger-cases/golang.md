# Trigger Cases: golang

## Positive (should activate)
- prompt: "I need help with this: Implementing or reviewing Go services/CLIs/libraries. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Designing or debugging concurrency (goroutines/channels/sync/context). Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is primarily another language/framework. No planning, just implementation."
  expect_activate: no
