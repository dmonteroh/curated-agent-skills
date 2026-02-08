# Trigger Cases: monorepo-engineering

## Positive (should activate)
- prompt: "I need help with this: Setting up a monorepo or migrating from polyrepo. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Making build/test/dev workflows faster (caching, affected detection). Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The repo is not a monorepo and there’s no plan to make it one. No planning, just implementation."
  expect_activate: no
