# Trigger Cases: research-discipline

## Positive (should activate)
- prompt: "Compare these three vector databases on pricing and rate limits and write it up for my team."
  expect_activate: yes

- prompt: "I'm making a purchasing decision off whatever you come back with, so I need to know which parts you actually verified and which you worked out yourself."
  expect_activate: yes

- prompt: "What do the current per-token prices look like for these two providers?"
  expect_activate: yes

- prompt: "Find out why our deploys started failing last Tuesday and report back what you found."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Apply this patch and run the test suite."
  expect_activate: no

- prompt: "I've already confirmed we need version 4.2. Just pin it in the lockfile."
  expect_activate: no

- prompt: "What does TTL stand for?"
  expect_activate: no
