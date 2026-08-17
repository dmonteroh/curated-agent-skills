# Trigger Cases: competitive-benchmark

## Positive (should activate)
- prompt: "We need to know who we're actually up against before the board meeting. Can you put together a proper competitive benchmark for us?"
  expect_activate: yes

- prompt: "Work out which studios contest the position we're going for, score them, and write it up so I can defend every number in the room."
  expect_activate: yes

- prompt: "I think there's an opening in the market for what we do, but I can't prove it. Is that space actually empty or is someone already sitting in it?"
  expect_activate: yes

- prompt: "Here are eleven companies someone threw at me. Which of these are real rivals, which are noise, and how do we compare across the board?"
  expect_activate: yes

- prompt: "Build the landscape report — tiers, a comparison matrix, deep dives on the interesting ones, and where our defensible ground is."
  expect_activate: yes

- prompt: "We keep losing deals to two firms and I don't know what they have that we don't. Can you compare us against them properly, with evidence?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "I already have the scoring spreadsheet from our consultant. Just turn it into a nice slide deck."
  expect_activate: no

- prompt: "We're picking between Postgres, DynamoDB and Cassandra for the event store. Which fits our read pattern best?"
  expect_activate: no

- prompt: "Review our own CLI and tell me how good the developer experience is."
  expect_activate: no

- prompt: "Give me a general overview of what's happening in the electric van market this year."
  expect_activate: no

- prompt: "Summarise these three vendor security questionnaires and flag anything that would fail our procurement checklist."
  expect_activate: no
