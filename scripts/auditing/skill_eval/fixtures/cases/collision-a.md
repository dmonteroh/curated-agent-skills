# Trigger Cases: collision-a

## Positive (should activate)
- prompt: "Help me write a heartfelt toast for my sister's wedding."
  expect_activate: yes
- prompt: "Give me talking points for a retirement speech."
  expect_activate: yes
- prompt: "Draft a eulogy for a close family friend."
  expect_activate: yes
- prompt: "Write a best-man speech with a few embarrassing stories."
  expect_activate: yes
- prompt: "Shared prompt used by both fixture skills for the collision test."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Book a table for four at the Italian place downtown."
  expect_activate: no
- prompt: "Summarize this week's team standup notes."
  expect_activate: no
- prompt: "Convert this CSV export into a formatted report."
  expect_activate: no
- prompt: "Draft an apology email to a delayed customer."
  expect_activate: no
- prompt: "Shared negative prompt claimed positive by the other fixture skill."
  expect_activate: no
