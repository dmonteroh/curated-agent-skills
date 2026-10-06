# Trigger Cases: mcp-server-development

## Positive (should activate)

- prompt: "I want to let Claude query our internal Postgres database for read-only reporting. Can you build an MCP server in TypeScript that exposes a run_query tool and a list_tables tool, with clear input schemas and helpful error messages when the SQL is invalid or the connection fails?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Please write a Python MCP server using the official SDK that gives an AI assistant tools to search, create, and close Jira tickets. Each tool needs a good description and parameter docs, and errors like auth failures or missing ticket IDs should come back with actionable messages."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Can you create an MCP server that exposes filesystem tools limited to a sandbox directory, such as read_file, write_file, and list_dir? Reject path traversal with clear error messages and use stdio transport so I can add it to Claude Desktop."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "build an mcp server for my notes app"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Build an MCP server that lets AI assistants call our internal customer lookup and order-status tools, with clear JSON schemas, descriptions, and actionable error messages."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Set up a Python server using the Model Context Protocol that exposes database-reporting tools to an AI assistant, with documented parameters and useful errors for invalid requests."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Turn our shipping-service endpoints into MCP tools for assistant use. Provide strong input validation, tool metadata, and errors that tell the model how to recover."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Can you write an MCP client in Python that connects to an existing MCP server over stdio, lists its tools, and calls one of them with arguments I pass on the command line?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Build a REST API in FastAPI for managing inventory items with CRUD endpoints, OpenAPI docs, and good error responses. No AI integration needed."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Explain what the Model Context Protocol is and how it differs from regular function calling. I just want a conceptual overview, with no code."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Build an MCP client that connects to existing tool servers and lets our assistant use their tools."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Convert our API into OpenAPI function definitions for a single LLM provider, with error handling."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Write a command-line tool that lets engineers query customer records and prints friendly error messages."
  expect_activate: no
  tags: [generated, gen:codex]
