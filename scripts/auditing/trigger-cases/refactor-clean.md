# Trigger Cases: refactor-clean

## Positive (should activate)
- prompt: "I need help with this: Refactoring tangled or hard-to-maintain code. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Reducing duplication, complexity, or code smells. Can you guide me?"
  expect_activate: yes

- prompt: "An agent generated a custom date picker and a hand-rolled debounce for us last week. Before I spend time tidying them, should either of them exist at all?"
  expect_activate: yes

- prompt: "Clean up just what my branch touched before I open the PR — same behaviour, nothing outside the diff."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: A small, targeted fix is all that is needed. No planning, just implementation."
  expect_activate: no

- prompt: "Rewrite this parser to be three times faster. I'll benchmark it afterwards and I don't need the output to match what it does today."
  expect_activate: no
