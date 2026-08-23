# Trigger Cases: ux-interview

## Positive (should activate)
- prompt: "Interview me about how I actually use our internal deploy tool, then write up what the next version has to support."
  expect_activate: yes

- prompt: "I want to spec out the new invoicing screen based on how the finance team works today. Can you talk to me through it and build the requirements from my answers?"
  expect_activate: yes

- prompt: "Before we redesign anything, ask me questions about my current workflow one at a time and save a transcript."
  expect_activate: yes

- prompt: "We keep guessing at what our support agents need. Run a proper user interview with me and give me a written spec at the end."
  expect_activate: yes

- prompt: "Here's the PRD. Interview our ops lead about the real process and tell me where the doc and the lived experience disagree."
  expect_activate: yes

- prompt: "Walk me through a discovery interview about the reimbursement portal — where it hurts, what I'd keep, what I work around."
  expect_activate: yes

## Negative (should not activate)
- prompt: "We haven't decided what the company stands for yet. Interview me about our values and positioning so we can pin down the brand first."
  expect_activate: no

- prompt: "Ask me questions until we land on the tone of voice and personality for the product, then write that up."
  expect_activate: no

- prompt: "Here's the clickable prototype. Give me five tasks to attempt and record where I get stuck and how long each takes."
  expect_activate: no

- prompt: "Let's brainstorm features for Q3 and rank them by impact."
  expect_activate: no

- prompt: "Quick question — do you think a modal or a side panel is better for this form?"
  expect_activate: no
