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

- prompt: "Create a Jira bug in the PAY project: checkout page throws a 500 when the cart has more than 20 items. Set priority to High and assign it to Dana Reyes."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Link WEB-310 as blocking WEB-325, and mark WEB-298 as a duplicate of WEB-301."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Update PROJ-184 with the reproduction steps from our incident review, change its status to Blocked, and link it to PROJ-201 as blocked by."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "create jira ticket for broken csv exports"
  expect_activate: yes
  tags: [generated, off-register, gen:codex]

## Negative (should not activate)
- prompt: "Reorder the backlog so the auth ticket sits above the reporting one."
  expect_activate: no

- prompt: "Write a Confluence page documenting our release process."
  expect_activate: no

- prompt: "Edit the Jira workflow so Done issues auto-close after 30 days."
  expect_activate: no

- prompt: "Create a GitHub issue in our repo for the flaky login test and label it as bug."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Break down this project plan into a Gantt-style timeline in a markdown table with weeks and milestones. We aren't putting it in any tracker yet."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Can you explain how issue links and workflow statuses work in Jira?"
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Draft a project plan for the analytics migration, including milestones, owners, and risks, but do not create any tickets."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Write a Python script that exports Jira issue data to CSV using the REST API so our analytics team can load it into a dashboard."
  expect_activate: no
  tags: [generated, gen:claude]
