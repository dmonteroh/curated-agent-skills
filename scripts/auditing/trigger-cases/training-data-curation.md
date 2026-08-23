# Trigger Cases: training-data-curation

## Positive (should activate)
- prompt: "I have about 12,000 graded agent runs from last quarter. How do I turn the good ones into a training set?"
  expect_activate: yes

- prompt: "Our fine-tuned model scores 94% on the eval set and nobody on the team believes the number. How would I check whether it's real?"
  expect_activate: yes

- prompt: "We're mixing roughly 30k generated examples with 5k collected ones. Anything we should verify before kicking off the run?"
  expect_activate: yes

- prompt: "This training set was built by three people over two months and nobody can tell me what's actually in it. Can you audit it?"
  expect_activate: yes

- prompt: "I need to reshape our existing SFT jsonl into chosen/rejected pairs. What do I need to watch out for?"
  expect_activate: yes

- prompt: "Loss curve looked completely normal but the checkpoint came out worse at the task. We enabled packing for the first time on this run."
  expect_activate: yes

## Negative (should not activate)
- prompt: "We have 5,000 raw production transcripts. Nobody has scored them yet — can you convert them straight into training rows?"
  expect_activate: no

- prompt: "I'm building the search index for our documentation. How should I split the documents into passages?"
  expect_activate: no

- prompt: "For this task, should we be using DPO or KTO?"
  expect_activate: no

- prompt: "We need to build the golden evaluation set for this project from scratch. Where do we start?"
  expect_activate: no

- prompt: "The dataset is done and carded. What batch size and gradient accumulation steps should the run use?"
  expect_activate: no
