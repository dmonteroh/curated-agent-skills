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

## Negative (should not activate)
- prompt: "It needs my authorization before it force-pushes. Can we auto-approve that one to save the round trip?"
  expect_activate: no

- prompt: "It's about to drop a production table and I'm looking for a way for it not to have to check with me."
  expect_activate: no

- prompt: "Quick one while I'm sitting here — tabs or spaces for this file?"
  expect_activate: no

- prompt: "Help me work out the right questions to put to the client about their requirements."
  expect_activate: no
