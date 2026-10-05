# Trigger Cases: skill-with-leak

## Positive (should activate)
- prompt: "We need to draft a rollback plan before the migration window closes tonight"
  expect_activate: yes

- prompt: "Help me prepare an incident rollback checklist for tonight's deploy"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Just write a poem about the ocean, nothing operational here"
  expect_activate: no
