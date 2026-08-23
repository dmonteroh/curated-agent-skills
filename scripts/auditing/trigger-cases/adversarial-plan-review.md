# Trigger Cases: adversarial-plan-review

## Positive (should activate)
- prompt: "We're about to run a one-way migration that rewrites every row in the users table. Here is the plan — I want it torn apart before we commit to it."
  expect_activate: yes

- prompt: "The team signed off on this API redesign in about ten minutes and nobody raised a single objection. That worries me more than it reassures me."
  expect_activate: yes

- prompt: "This whole architecture doc came out of one drafting pass and nothing in it has ever been contradicted. Can we stress it properly before we build?"
  expect_activate: yes

- prompt: "The proposal keeps trading coverage away for simplicity, and I want those tensions argued out in the open rather than smoothed over by one voice."
  expect_activate: yes

- prompt: "I need more than a verdict on this design — I need a written record of which objections it survived and why, for the decision log."
  expect_activate: yes

## Negative (should not activate)
- prompt: "We still haven't agreed on what this feature is even supposed to do. Help me pin the goal down first."
  expect_activate: no

- prompt: "The migration approach is settled and signed off. Just help me write the first batch of the script."
  expect_activate: no

- prompt: "One open question: does this refactor break the existing test suite or not?"
  expect_activate: no
