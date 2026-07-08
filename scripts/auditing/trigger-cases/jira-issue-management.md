# Trigger Cases: jira-issue-management

## Positive (should activate)
- prompt: "Create a Jira epic for the dashboard plan with one task per phase."
  expect_activate: yes

- prompt: "Move SHL-42 to In Progress in Jira."
  expect_activate: yes

- prompt: "Search Jira for open tasks under the reporting epic and summarize them."
  expect_activate: yes

- prompt: "Bootstrap the Jira project map file for this repo."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Reorder the backlog so the auth ticket sits above the reporting one."
  expect_activate: no

- prompt: "Write a Confluence page documenting our release process."
  expect_activate: no

- prompt: "Edit the Jira workflow so Done issues auto-close after 30 days."
  expect_activate: no
