# Trigger Cases: pr-description

## Positive (should activate)
- prompt: "Draft the PR description for this branch — the task brief is in docs/briefs/checklist-export.md."
  expect_activate: yes

- prompt: "Write a pull request body for my feature branch against develop."
  expect_activate: yes

- prompt: "The description on this PR is stale after the latest commits; refresh it."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Write a commit message for these staged changes."
  expect_activate: no

- prompt: "Create the pull request on GitHub and merge it once CI is green."
  expect_activate: no

- prompt: "Summarize the diff file by file so I can review it."
  expect_activate: no
