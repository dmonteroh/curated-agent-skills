# Trigger Cases: javascript

## Positive (should activate)
- prompt: "I need help with this: Building modern JavaScript for Node.js or browsers. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Debugging async behavior, event loops, or performance. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The user needs TypeScript architecture guidance. No planning, just implementation."
  expect_activate: no
