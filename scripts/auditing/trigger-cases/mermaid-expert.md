# Trigger Cases: mermaid-expert

## Positive (should activate)
- prompt: "I need help with this: Mermaid diagram code is needed for system, process, or data visuals. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Guidance is needed to select the right Mermaid diagram type and syntax. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The request is not about Mermaid diagrams or diagram structure. No planning, just implementation."
  expect_activate: no
