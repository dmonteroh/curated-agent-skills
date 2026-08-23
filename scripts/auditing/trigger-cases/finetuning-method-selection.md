# Trigger Cases: finetuning-method-selection

## Positive (should activate)
- prompt: "Leadership wants the model fine-tuned on our internal docs so it can answer support questions about them. Where do we start?"
  expect_activate: yes

- prompt: "I've got about 4,000 thumbs-up/thumbs-down clicks from reviewers on individual responses. Can I turn that into a DPO run?"
  expect_activate: yes

- prompt: "The team is split between DPO and GRPO for our code-fix task. We can run the test suite to check whether a patch is correct automatically."
  expect_activate: yes

- prompt: "Planning a LoRA tune of an 8B-class model on a 48GB card. Will it fit, and is LoRA even the right approach for what we're trying to change?"
  expect_activate: yes

- prompt: "Our GRPO run finished and now the model writes enormous answers that score great and are mostly wrong. What did we get wrong upstream?"
  expect_activate: yes

- prompt: "We want the assistant to follow our support macros exactly instead of improvising. Is that a training problem?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "We've settled on LoRA for this one. What rank and learning rate should I set, and how many epochs?"
  expect_activate: no

- prompt: "Model's trained and passing eval. I need the rollout plan — canary percentages, promotion gate, and how we roll back if latency spikes."
  expect_activate: no

- prompt: "Our RAG answers are bad. How should I chunk these docs, and what should I use for reranking?"
  expect_activate: no

- prompt: "Rewrite this system prompt so the agent stops asking three clarifying questions before it does anything."
  expect_activate: no

- prompt: "Which quantization format should we export the finished checkpoint to for the edge boxes?"
  expect_activate: no
