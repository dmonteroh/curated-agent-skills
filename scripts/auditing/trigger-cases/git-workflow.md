# Trigger Cases: git-workflow

## Positive (should activate)
- prompt: "I need help with this: Preparing a clean PR (commit messages, splitting/squashing, rebase onto main). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Resolving merge conflicts or untangling diverged branches. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: No Git repository is available. No planning, just implementation."
  expect_activate: no
