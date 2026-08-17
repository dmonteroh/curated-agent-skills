# Trigger Cases: architect-review

## Positive (should activate)
- prompt: "I need help with this: Reviewing system architecture or major design changes. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Evaluating scalability, resilience, or maintainability impacts. Can you guide me?"
  expect_activate: yes

- prompt: "Our domain layer is importing from the HTTP controllers now, and billing has started reading orders' tables directly. Is this as bad as it looks?"
  expect_activate: yes

- prompt: "This aggregate has grown to eleven entities and every transaction locks the whole thing. Is it the right size, or should it be split?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is a small code review without architectural impact. No planning, just implementation."
  expect_activate: no
