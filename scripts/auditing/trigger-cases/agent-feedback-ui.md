# Trigger Cases: agent-feedback-ui

## Positive (should activate)
- prompt: "You generated eight candidate chart layouts. I want to score each one and leave a short note before you carry on."
  expect_activate: yes

- prompt: "These four rendered mockups can't be judged from a text description — I need them side by side at full size so I can pick one."
  expect_activate: yes

- prompt: "For each of these ten generated headlines give me a 1-5 rating field and a comment box, then take the whole set back at once."
  expect_activate: yes

- prompt: "If I dislike every candidate I want to reject the batch and get a fresh set, without you asking me about them one at a time in chat."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Just ask me straight: do I want option A or option B? One word answer."
  expect_activate: no

- prompt: "Interview me about what I want out of this dashboard, following up based on whatever I say."
  expect_activate: no

- prompt: "My ratings are already sitting in results.json from the last round — read those and continue."
  expect_activate: no
