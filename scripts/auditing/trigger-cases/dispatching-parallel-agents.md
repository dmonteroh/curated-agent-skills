# Trigger Cases: dispatching-parallel-agents

## Positive (should activate)
- prompt: "Requirements are unclear and we need help comparing options before implementation."
  expect_activate: yes

- prompt: "Requirements are unclear and we need help comparing options before implementation."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Implement this exact feature now; requirements are final and no design/exploration is needed."
  expect_activate: no
