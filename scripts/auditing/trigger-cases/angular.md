# Trigger Cases: angular

## Positive (should activate)
- prompt: "I need help with this: Building/refactoring Angular components (standalone + signals). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Choosing state strategy (signals vs RxJS vs NgRx) and keeping it consistent. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The project is not Angular. No planning, just implementation."
  expect_activate: no
