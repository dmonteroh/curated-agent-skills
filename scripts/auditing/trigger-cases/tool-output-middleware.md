# Trigger Cases: tool-output-middleware

## Positive (should activate)
- prompt: "Our MCP handlers return enormous blobs. I want to trim them before they reach the model without losing the one line that mattered."
  expect_activate: yes

- prompt: "I'm wrapping kubectl so its output gets grouped and deduplicated before it lands in the transcript."
  expect_activate: yes

- prompt: "Tool output occasionally contains API keys. Strip them on the way into context."
  expect_activate: yes

- prompt: "Retrieved documents blow the prompt budget, so I need them summarized before they get inserted."
  expect_activate: yes

- prompt: "We already have a filter sitting in front of the model. I want it reviewed for what it does under pathological input."
  expect_activate: yes

## Negative (should not activate)
- prompt: "I'm switching the tool's output from pretty-printed JSON to compact JSON."
  expect_activate: no

- prompt: "Make our CLI's log output nicer to read for the humans watching the terminal."
  expect_activate: no

- prompt: "I own the query and could just narrow it. Should I add a filtering layer in front instead?"
  expect_activate: no

- prompt: "The tool returns a single status line and its contract caps it there."
  expect_activate: no
