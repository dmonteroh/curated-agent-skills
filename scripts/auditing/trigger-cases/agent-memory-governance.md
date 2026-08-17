# Trigger Cases: agent-memory-governance

## Positive (should activate)
- prompt: "I'm building a learnings file the agent appends to at the end of every session and reloads at the start of the next one. What could go wrong with that?"
  expect_activate: yes

- prompt: "A preference the agent picked up on one project is about to be written into the profile that loads on every project. Should it be?"
  expect_activate: yes

- prompt: "The user just said 'never ask me about formatting again'. How should that turn into a durable record the agent honours later?"
  expect_activate: yes

- prompt: "Our agent writes project notes right after reading GitHub issue bodies and fetched pages. Someone pointed out that's an attack surface."
  expect_activate: yes

- prompt: "After a compaction the agent resumes from a checkpoint file an earlier session wrote. How much should it trust what's in there?"
  expect_activate: yes

- prompt: "The agent has started inferring my preferences from what I do rather than what I've told it, and writing those inferences down."
  expect_activate: yes

## Negative (should not activate)
- prompt: "The agent loads our hand-written engineering handbook at startup and it's getting heavy. Help me decide which pages it still needs."
  expect_activate: no

- prompt: "These scratch notes only exist for the length of one run and get thrown away at the end."
  expect_activate: no

- prompt: "Where should the agent stash the API token so it can reuse it in the next session?"
  expect_activate: no
