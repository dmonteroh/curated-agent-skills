# Trigger Cases: brainstorming

## Positive (should activate)
- prompt: "I'm not sure which architecture to choose. Can you help me decide between options?"
  expect_activate: yes

- prompt: "Requirements are still fuzzy. Let's do a quick design brief before coding."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Implement this exact API endpoint now; requirements are final and no design work is needed."
  expect_activate: no
