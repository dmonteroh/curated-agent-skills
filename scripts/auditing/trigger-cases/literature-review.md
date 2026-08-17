# Trigger Cases: literature-review

## Positive (should activate)
- prompt: "I'm writing the related-work section for a paper on retrieval-augmented generation. Find the relevant work, screen it, and tell me what the state of the art actually is."
  expect_activate: yes

- prompt: "What does the published evidence say about gene-editing therapies for sickle cell disease? My supervisor needs to be able to re-run whatever searches I did."
  expect_activate: yes

- prompt: "Pull together the studies on remote-work productivity and tell me which findings actually hold up versus which come from one small sample."
  expect_activate: yes

- prompt: "I need a scoping review of methods for detecting label noise in training data, with the search strings and exclusions recorded."
  expect_activate: yes

- prompt: "I exported a couple of hundred records from two databases on this topic. Deduplicate them, screen them, and synthesize what's left."
  expect_activate: yes

- prompt: "Where does the literature on transformer efficiency benchmarks contradict itself, and what has nobody measured yet?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "What year was the original transformer paper published, and who were the authors?"
  expect_activate: no

- prompt: "Roughly speaking, does the research think microservices reduce deployment risk? Just a quick sense of it, I'm not writing anything."
  expect_activate: no

- prompt: "Here's the draft of my thesis chapter. Read it and tell me what to fix before I send it to my advisor."
  expect_activate: no

- prompt: "Which vendors sell managed vector databases, and what do they charge?"
  expect_activate: no

- prompt: "Convert these 40 references to APA style and check that the formatting is consistent."
  expect_activate: no
