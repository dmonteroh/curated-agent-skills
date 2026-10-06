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

- prompt: "Who owns this patent now? I've got a page from a patent aggregator saying one thing and I need to know whether that's good enough to act on."
  expect_activate: yes

- prompt: "Go find what people are saying about Tella and write it up — heads up, the name collides with a footballer and half a dozen other things."
  expect_activate: yes

- prompt: "Last time two of the sources you tried timed out and you came back saying there was nothing out there. I need to be able to tell those two situations apart."
  expect_activate: yes

- prompt: "findings doc for the auth bug pls label sourced vs from me vs speculation"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Write up what we learned about the memory leak in the worker service. Mark what's backed by the heap dumps and code you read, what I told you from memory about when it started, and what's speculation about root cause. My manager will read it and needs to know how much to trust each part."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Prepare a due-diligence memo that makes it obvious which conclusions are supported by documents, which came from the requester, and which remain speculative."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "Apply this patch and run the test suite."
  expect_activate: no

- prompt: "I've already confirmed we need version 4.2. Just pin it in the lockfile."
  expect_activate: no

- prompt: "What does TTL stand for?"
  expect_activate: no

- prompt: "Read the retry limit straight out of config/settings.yml and tell me the number. Nothing else."
  expect_activate: no

- prompt: "Write a postmortem template our team can reuse for incidents, with sections for timeline, impact, root cause, and action items."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Review my draft incident report for grammar and tone, and tighten the wording without changing the content."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Add citations to the bibliography in my literature review so each claim links to a numbered reference in APA format."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Write a confidence-interval section for my A/B test analysis explaining the statistical uncertainty in the conversion lift estimate."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]
