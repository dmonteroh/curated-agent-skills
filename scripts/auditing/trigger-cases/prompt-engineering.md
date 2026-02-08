# Trigger Cases: prompt-engineering

## Positive (should activate)
- prompt: "I need help with this: Building AI features and agent behaviors (system prompts, tool-use prompts, routing). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Improving output quality, consistency, safety, or cost/latency. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The user only wants an ad-hoc explanation of prompting concepts. No planning, just implementation."
  expect_activate: no
