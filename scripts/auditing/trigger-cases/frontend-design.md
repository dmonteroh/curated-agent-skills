# Trigger Cases: frontend-design

## Positive (should activate)
- prompt: "I need help with this: Building or styling frontend UI with real code (HTML/CSS/JS, React, Vue, etc.). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: The user expects a distinct aesthetic direction and production-grade polish. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is design critique or high-level UI feedback without implementation. No planning, just implementation."
  expect_activate: no
