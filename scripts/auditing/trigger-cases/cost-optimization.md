# Trigger Cases: cost-optimization

## Positive (should activate)
- prompt: "I need help with this: A team needs to reduce cloud spend (quick wins + longer-term program). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: A team needs tagging/label standards and cost allocation. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The request is for cloud architecture/platform selection or migrations. No planning, just implementation."
  expect_activate: no
