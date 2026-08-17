# Trigger Cases: frontend-design

## Positive (should activate)
- prompt: "I need help with this: Building or styling frontend UI with real code (HTML/CSS/JS, React, Vue, etc.). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: The user expects a distinct aesthetic direction and production-grade polish. Can you guide me?"
  expect_activate: yes

- prompt: "Our dashboard has a fixed sidebar and header, but the whole window scrolls instead of just the content pane. Can you rebuild the shell so scrolling lands in the right place?"
  expect_activate: yes

- prompt: "The settings screen looked great with placeholder text. With real customer data the names wrap into three lines and one long URL blows the column out. Make it hold up."
  expect_activate: yes

- prompt: "The play icons in our toolbar look a hair off-centre, and the panel swap animation snaps if you click fast. Tighten the polish pass."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is design critique or high-level UI feedback without implementation. No planning, just implementation."
  expect_activate: no
