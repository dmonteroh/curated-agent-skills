# Trigger Cases: cdd-context

## Positive (should activate)
- prompt: "Our error strings are all over the place — some say 'Oops!', some dump a stack trace. Where do we write down how the product is supposed to sound so everyone follows it?"
  expect_activate: yes

- prompt: "I inherited this repo and nothing about the stack, the domain or the release process is written down anywhere. Can we pull that out of the code itself?"
  expect_activate: yes

- prompt: "There's no docs/context folder in this repo at all. Can you set up the context docs and an index for them?"
  expect_activate: yes

- prompt: "We moved off MySQL onto Postgres and switched to trunk-based development last month. Can you bring the tech stack and workflow context docs up to date?"
  expect_activate: yes

- prompt: "Our product direction changed this quarter — we're aiming at enterprise teams now instead of solo developers. Update the product context to match."
  expect_activate: yes

- prompt: "Can you write a short snapshot of this project I can paste at the start of a session so a new teammate or agent gets back up to speed fast?"
  expect_activate: yes

- prompt: "refresh our product and tech background docs"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

## Negative (should not activate)
- prompt: "We already have a README, an architecture doc and an ADR folder that mostly work. I don't want another set of files — I want to decide which of those owns what and keep them from drifting apart."
  expect_activate: no

- prompt: "Save a note to your memory that I prefer tabs over spaces and terse commit messages."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Generate a CHANGELOG entry for the 2.4.0 release based on the commits since the last tag."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Create a detailed architecture decision record explaining why we chose PostgreSQL over MongoDB."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Write a postmortem for last week’s production outage and list the corrective actions."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Implement a new employee onboarding portal with accounts, checklists, and progress tracking."
  expect_activate: no
  tags: [generated, gen:codex]
