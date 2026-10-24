# Trigger Cases: interruption-budget

## Positive (should activate)
- prompt: "You stop and ask me the same kind of thing five times a run, and most of them have an obvious default. Curb that."
  expect_activate: yes

- prompt: "I have eleven candidates to choose between and the question tool only accepts four options. Don't just drop the rest."
  expect_activate: yes

- prompt: "This run will pause and ask me at maybe eight different points. I want those shaped before it starts, not improvised."
  expect_activate: yes

- prompt: "There's no human attached to this run and the ask-the-user channel errors out. What happens to a question then?"
  expect_activate: yes

- prompt: "I want every question in this workflow declared up front and tagged by whether its answer can be undone."
  expect_activate: yes

- prompt: "Our agent needs to ask the user a clarifying question when a request is ambiguous. Give me a template for phrasing those questions so someone can answer in one tap or one word, with a default option included."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Create a practical policy for deciding when our support agent should ask a human for clarification versus make a reasonable assumption, with examples of concise questions it should ask."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "when should my agent ask me vs just decide"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

## Negative (should not activate)
- prompt: "It needs my authorization before it force-pushes. Can we auto-approve that one to save the round trip?"
  expect_activate: no

- prompt: "It's about to drop a production table and I'm looking for a way for it not to have to check with me."
  expect_activate: no

- prompt: "Quick one while I'm sitting here — tabs or spaces for this file?"
  expect_activate: no

- prompt: "Help me work out the right questions to put to the client about their requirements."
  expect_activate: no

- prompt: "Write a survey questionnaire for our users about the onboarding flow, with questions phrased so they're quick to answer."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "How should I decide when a human manager should step in versus letting the junior engineers decide on their own for production incidents?"
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Create a rubric for grading whether an AI assistant gave a helpful answer."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Design a chatbot personality guide that makes responses warmer and more conversational."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Help me design retry and timeout logic for my agent's tool calls so it recovers gracefully when an API fails."
  expect_activate: no
  tags: [generated, gen:claude]
