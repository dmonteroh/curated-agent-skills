# Trigger Cases: gdpr-data-handling

## Positive (should activate)
- prompt: "I need help with this: Building systems that process EU personal data. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Establishing lawful basis + purpose limitation and mapping data flows. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is unrelated to GDPR data handling. No planning, just implementation."
  expect_activate: no
