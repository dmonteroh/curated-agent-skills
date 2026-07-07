# Trigger Cases: ux-interview

## Positive (should activate)
- prompt: "I need help with this: The user wants a UX-style interview about real usage of a product, system, or workflow. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: The goal is discovery of current-state behavior, not immediate solution design. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The user asks for brainstorming, feature ideation, or roadmap prioritization without a discovery interview. No planning, just implementation."
  expect_activate: no
