# Trigger Cases: cdd-context

## Positive (should activate)
- prompt: "I need help with this: Starting work in a repo and stable context (what/why/how) is needed before making changes. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: A team wants consistent, discoverable context artifacts for humans and agents. Can you guide me?"
  expect_activate: yes

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

## Negative (should not activate)
- prompt: "Please do this exactly now: The request is a one-line change and context is already clear. No planning, just implementation."
  expect_activate: no

- prompt: "We already have a README, an architecture doc and an ADR folder that mostly work. I don't want another set of files — I want to decide which of those owns what and keep them from drifting apart."
  expect_activate: no
