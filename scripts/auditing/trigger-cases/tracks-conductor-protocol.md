# Trigger Cases: tracks-conductor-protocol

## Positive (should activate)
- prompt: "We finished the whole track but the plan doesn't record which commits actually implemented which task. How do I make that auditable after the fact?"
  expect_activate: yes

- prompt: "Halfway through we changed approach and nobody wrote it down. Which artifact is supposed to absorb a deviation like that?"
  expect_activate: yes

- prompt: "I've got a rough idea for adding SSO login to our app. Can you turn it into a task brief, then write the spec and plan, and make sure the task index is updated as it moves along?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "The spec for task 014 is approved. Write the implementation plan, execute it, and update the index so the status reflects what's done."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "new task idea dark mode brief it then spec and plan"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Take these product ideas through the structured repository workflow from initial brief through specification, planning, implementation, and index maintenance."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Please run our full work-tracking pipeline for the backlog: capture the ideas as briefs, develop approved briefs into specs and plans, carry out the planned work, and synchronize the task index."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Can you set up a Jira board with sprints and swimlanes for my team? I want to compare Jira with Linear first."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Refactor the payment module to remove duplicated validation logic. No need for any briefs or specs, just do it."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Add a TODO list at the top of main.py with the things I still need to fix in that file."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Explain the difference between a design doc, an RFC, and an ADR, and which one is best for a database migration decision."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Migrate our existing GitHub issues and labels into a new project board, preserving assignees, milestones, and due dates."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Create a release checklist and changelog process for this repository, including version tagging and deployment approval steps."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Build a dashboard that reports sprint velocity, open bugs, and team workload from our issue tracker."
  expect_activate: no
  tags: [generated, gen:codex]
