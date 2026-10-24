# Trigger Cases: residue

## Positive (should activate)
- prompt: "I need help with this: Making a decision that affects architecture boundaries. Can you guide me?"
  expect_activate: yes
- prompt: "How long should I proof sourdough bread before baking?"
  expect_activate: yes
- prompt: "What hydration ratio works best for a beginner loaf?"
  expect_activate: yes
- prompt: "My starter smells like nail polish, is it still usable?"
  expect_activate: yes
- prompt: "Suggest a baking schedule for a same-day sourdough loaf."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: Capturing minor implementation notes. No planning, just implementation."
  expect_activate: no
- prompt: "Summarize this week's team standup notes."
  expect_activate: no
- prompt: "Convert this CSV export into a formatted report."
  expect_activate: no
- prompt: "Draft an apology email to a delayed customer."
  expect_activate: no
- prompt: "Reset the CI cache and rerun the failing pipeline."
  expect_activate: no
