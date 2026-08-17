# Trigger Cases: ui-design

## Positive (should activate)
- prompt: "I need help with this: Requirements are unclear and you need a UI brief + flow before implementation. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Defining component behaviors and states (loading/empty/error/disabled). Can you guide me?"
  expect_activate: yes

- prompt: "We're building an internal invoicing tool. There's no brand, no colours, no reference material, and honestly I don't know what I want it to look like. Where do we start?"
  expect_activate: yes

- prompt: "You showed me three directions and I picked the second one. The header feels heavy and the cards are louder than the data — let's do another round on it."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The user explicitly wants UI code implementation only. No planning, just implementation."
  expect_activate: no

- prompt: "Marketing signed off on the brand kit last month. Just apply those tokens to the new screens — don't propose anything else."
  expect_activate: no
