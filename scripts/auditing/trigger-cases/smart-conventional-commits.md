# Trigger Cases: smart-conventional-commits

## Positive (should activate)
- prompt: "Commit these changes with a good message."
  expect_activate: yes

- prompt: "Draft a conventional commit message for what I just changed — it adds an on-demand PDF download button."
  expect_activate: yes

- prompt: "Commit the unstaged changes; keep the message consistent with this repo's commit style."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Write a pull request description for this branch."
  expect_activate: no

- prompt: "Review the last five commits and tell me what changed."
  expect_activate: no

- prompt: "Squash and rewrite the history on main to clean it up."
  expect_activate: no
