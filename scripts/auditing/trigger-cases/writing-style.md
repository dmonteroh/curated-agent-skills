# Trigger Cases: writing-style

## Positive (should activate)
- prompt: "Write up the migration plan from these notes so the platform team can run it without me on the call."
  expect_activate: yes

- prompt: "These error strings are all over the place. Some say 'unable to', some say 'failed to', some just say 'error'. Sort them out."
  expect_activate: yes

- prompt: "Draft the tool descriptions for these six MCP tools. Another agent is the only thing that reads them."
  expect_activate: yes

- prompt: "Our docs are written by four different people across a year and it shows. Bring the runbook section into one voice."
  expect_activate: yes

- prompt: "Write the PR body and the changelog entry for this branch."
  expect_activate: yes

- prompt: "apply STE100 to this"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Write the launch post for the new caching layer. Make it land on Hacker News."
  expect_activate: no

- prompt: "Clean up the phrasing in these support-ticket quotes before I paste them into the deck."
  expect_activate: no

- prompt: "This README reads like a machine wrote it. Make it sound like a person again."
  expect_activate: no

- prompt: "Here are eighteen of my published posts. Work out my house voice from them and write it up."
  expect_activate: no

- prompt: "Just answer me directly: does the retry budget include the initial attempt or not?"
  expect_activate: no
  # Measured, not assumed: no description tested makes a skill load for an
  # interactive reply, 0 of 24 traced runs. The skill's `conversation` profile
  # still governs a reply the moment the skill is loaded for some other reason.

- prompt: "Add more comments to this file, there aren't enough."
  expect_activate: no
  # The ask is about how many comments exist. This skill governs the register of
  # the comments that get written and never their number.
