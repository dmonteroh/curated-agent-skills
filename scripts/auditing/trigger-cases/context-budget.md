# Trigger Cases: context-budget

## Positive (should activate)
- prompt: "Every session starts about a third full before I've typed a word, and I have no idea what's sitting in there."
  expect_activate: yes

- prompt: "We've bolted on four instruction files and a dozen tool integrations over the past year and nobody has ever priced the result."
  expect_activate: yes

- prompt: "Does this 600-word convention belong in the file that always loads, or behind something the agent pulls in only when it needs it?"
  expect_activate: yes

- prompt: "I inherited someone else's agent configuration and can't tell what it loads up front or why any of it is there."
  expect_activate: yes

- prompt: "I want to wire in two more tool servers. Is there actually room, or are we already too heavy before the first message?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "The run fell apart right after I had you read a 40,000-line log file."
  expect_activate: no

- prompt: "This session has degraded badly over the last hour and I need it working again right now."
  expect_activate: no

- prompt: "Our monthly API bill has doubled and I want to bring the spend down."
  expect_activate: no

- prompt: "Tell me whether our 400-token safety instruction is worth what it costs us."
  expect_activate: no
