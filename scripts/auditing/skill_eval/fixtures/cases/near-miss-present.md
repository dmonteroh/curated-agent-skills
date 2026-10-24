# Trigger Cases: near-miss-present

## Positive (should activate)
- prompt: "Walk me through starting a sourdough starter from scratch."
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
- prompt: "Recommend a good pizza dough troubleshooting guide for beginners."
  expect_activate: no
- prompt: "Book a table for four at the Italian place downtown."
  expect_activate: no
- prompt: "Summarize this week's team standup notes."
  expect_activate: no
- prompt: "Convert this CSV export into a formatted report."
  expect_activate: no
- prompt: "Draft an apology email to a delayed customer."
  expect_activate: no
