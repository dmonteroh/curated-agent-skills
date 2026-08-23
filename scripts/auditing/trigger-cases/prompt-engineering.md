# Trigger Cases: prompt-engineering

## Positive (should activate)
- prompt: "I need help with this: Building AI features and agent behaviors (system prompts, tool-use prompts, routing). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Improving output quality, consistency, safety, or cost/latency. Can you guide me?"
  expect_activate: yes

- prompt: "We're upgrading from an older model to Claude Opus 4.8 — can you rework our system prompt so it performs well on the new model?"
  expect_activate: yes

- prompt: "Our agent on Sonnet 5 keeps ignoring the output format and calls tools too eagerly. Help me fix the prompt."
  expect_activate: yes

- prompt: "Design a prompt template library with regression tests for our extraction pipeline."
  expect_activate: yes

- prompt: "Write a system prompt for our GPT-based support bot that must return strict JSON and never leak internal data."
  expect_activate: yes

- prompt: "One call gets this classification wrong maybe 15% of the time. Could we run it several times and take the most common answer, and report how much they agreed?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The user only wants an ad-hoc explanation of prompting concepts. No planning, just implementation."
  expect_activate: no

- prompt: "Which Python SDK should I use to call the model, and how do I set up the API client?"
  expect_activate: no
