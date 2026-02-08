# Trigger Cases: mcp-server-development

## Positive (should activate)
- prompt: "I need help with this: Designing an MCP server tool surface (not just wrapping REST endpoints). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Implementing an MCP server in Node/TypeScript or Python. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: You only need to call existing tools without new MCP server work. No planning, just implementation."
  expect_activate: no
