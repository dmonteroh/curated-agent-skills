# Trigger Cases: shell-scripting

## Positive (should activate)
- prompt: "I need help with this: Writing Bash or POSIX shell scripts for automation. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Building CI/CD helpers, installers, or local tooling. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task requires another language runtime or SDK. No planning, just implementation."
  expect_activate: no
