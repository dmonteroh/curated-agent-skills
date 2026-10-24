# Trigger Cases: prompt-engineering

## Positive (should activate)
- prompt: "We're upgrading from an older model to Claude Opus 4.8 — can you rework our system prompt so it performs well on the new model?"
  expect_activate: yes

- prompt: "Our agent on Sonnet 5 keeps ignoring the output format and calls tools too eagerly. Help me fix the prompt."
  expect_activate: yes

- prompt: "Design a prompt template library with regression tests for our extraction pipeline."
  expect_activate: yes

- prompt: "Write a system prompt for our GPT-based support bot that must return strict JSON and never leak internal data."
  expect_activate: yes

- prompt: "One call gets this classification wrong maybe 15% of the time. Could we run it several times and take the most common answer, and report how much they agreed?"
  expect_activate: yes

- prompt: "fix my bot system prompt its too rude to customers"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Write a system prompt for a voice assistant in our car infotainment system. It needs to keep answers to one or two sentences, refuse to do anything distracting while the car is moving, and handle ambiguous commands by asking one short clarifying question."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "The system prompt for our in-app SQL helper is 900 lines of accumulated patches and the model ignores half of it. Can you refactor it into something tighter and test that the behavior doesn't regress on the 20 sample queries in evals/sql_cases.json?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Rewrite the system prompt for our support chatbot, add adversarial test cases, and iterate until its escalation behavior is reliable."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Create a versioned prompt spec for the model in our product, run an evaluation set against it, and tune the instructions based on failures."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "Which Python SDK should I use to call the model, and how do I set up the API client?"
  expect_activate: no

- prompt: "Can you explain how system prompts differ from user messages in the Claude API, and how prompt caching works with them? I'm just trying to understand the concepts for a talk."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Write a job description and interview rubric for hiring a prompt engineer at our startup."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Improve the help-center article that documents how our AI assistant works."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Please fine-tune a classifier on our support tickets to predict urgency. Walk me through preparing the dataset and training loop with scikit-learn."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Fine-tune our customer-support model on last year's resolved ticket data."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Set up analytics dashboards to measure latency, retention, and thumbs-up rates for the AI feature."
  expect_activate: no
  tags: [generated, gen:codex]
