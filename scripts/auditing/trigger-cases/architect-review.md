# Trigger Cases: architect-review

## Positive (should activate)
- prompt: "I need help with this: Reviewing system architecture or major design changes. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Evaluating scalability, resilience, or maintainability impacts. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is a small code review without architectural impact. No planning, just implementation."
  expect_activate: no
