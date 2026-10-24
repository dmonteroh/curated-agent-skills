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

- prompt: "agent tool output too long need filter that keeps the error line"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Our coding agent runs pytest and the 4000-line output eats its whole context window. Can you design a post-processing layer for tool results that truncates the output but always keeps the failing assertion and traceback lines?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Build a middleware layer that condenses tool responses before they enter the agent context, while preserving the specific lines most likely to answer the agent’s question."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "I'm switching the tool's output from pretty-printed JSON to compact JSON."
  expect_activate: no

- prompt: "Make our CLI's log output nicer to read for the humans watching the terminal."
  expect_activate: no

- prompt: "I own the query and could just narrow it. Should I add a filtering layer in front instead?"
  expect_activate: no

- prompt: "The tool returns a single status line and its contract caps it there."
  expect_activate: no

- prompt: "Our agent's conversation history is getting too long. Design a summarization strategy that compresses older user and assistant turns into a running summary."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Write a log-rotation and retention config for our servers so that application logs older than 14 days are compressed and then deleted."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Add a masking step to our database export script so that customer emails are anonymized in the CSV we hand to the analytics team."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Improve the agent’s prompt so it asks tools more precise questions and receives smaller responses in the first place."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Summarize the agent’s final answer for the end user, keeping the most important sentence."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
