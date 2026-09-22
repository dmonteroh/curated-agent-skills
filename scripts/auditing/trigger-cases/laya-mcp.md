# Trigger Cases: laya-mcp

## Positive (should activate)

- prompt: "Classify this support ticket into one of our five queues and give me a confidence I can threshold on, instead of just picking one."
  expect_activate: yes

- prompt: "I need a fast, typed decision about this piece of text — pick a severity level on a fixed scale with a probability per level, not a paragraph."
  expect_activate: yes

- prompt: "This same routing question runs on every inbound message. I want something faster and cheaper than another LLM call to answer it."
  expect_activate: yes

- prompt: "Before handing this subtask off, score whether it needs deep reasoning or is a quick lookup, with a number I can branch on."
  expect_activate: yes

- prompt: "Test whether this statement is true or false about the text, and give me the probability, not just yes or no."
  expect_activate: yes

- prompt: "This decision model has a couple of checkpoints loaded. Which one should answer a question about whether the agent actually ran the tests?"
  expect_activate: yes

- prompt: "The call came back saying part of my input was cut. What do I do about it?"
  expect_activate: yes

## Negative (should not activate)

- prompt: "Summarize this support thread into a two-paragraph handoff note for the next agent."
  expect_activate: no

- prompt: "I don't know yet what the possible categories even are — help me figure out a taxonomy for these tickets first."
  expect_activate: no

- prompt: "Decide whether we should build a regex parser or route these records to a model at all, and design the escalation path."
  expect_activate: no

- prompt: "This is a one-off judgment call I need to make right now myself — is this email spam or not?"
  expect_activate: no

- prompt: "Rewrite this paragraph to be more concise."
  expect_activate: no
