# Trigger Cases: deterministic-extraction-gate

## Positive (should activate)
- prompt: "We have about 40,000 exported invoice lines in a fairly consistent text layout. Should I write a parser or just send each one to a model?"
  expect_activate: yes

- prompt: "Our extraction job calls a model once per record and the bill is getting silly. Most of these records look identical. Can we do this cheaper without losing accuracy?"
  expect_activate: yes

- prompt: "I want a hybrid pipeline: regex first, model only for the ones the regex struggles with. How do I decide which ones those are?"
  expect_activate: yes

- prompt: "My parser reports a 98% success rate but I have no idea how many rows it got wrong without noticing. How do I actually measure that?"
  expect_activate: yes

- prompt: "These log lines mostly follow one shape but some don't. What's the right way to pull the fields out and not silently drop the odd ones?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "These meeting notes are all over the place — no fixed structure at all. Pull out the action items and owners."
  expect_activate: no

- prompt: "I need to trim noisy CLI output before it goes into the agent's context so it doesn't blow the window. What should the filter keep?"
  expect_activate: no

- prompt: "Read this JSON payload and tell me what the settlement_status field means."
  expect_activate: no

- prompt: "We're extracting figures out of scanned court filings for a compliance submission. Every one has to be right. Build the pipeline."
  expect_activate: no

- prompt: "Here are three receipts. Just give me the totals."
  expect_activate: no
