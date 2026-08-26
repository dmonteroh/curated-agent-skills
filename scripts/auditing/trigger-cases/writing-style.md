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
  # Vendor-split, measured: claude never loads a skill on an interactive reply
  # (0 of 48 traced runs, any description); codex loads this one on every plain
  # question (24 of 24) and the reply rules in SKILL.md govern it there. "No"
  # here records the claude behaviour and the design intent that a reply needs
  # no activation: the always-on block is the chat mechanism on both vendors.

- prompt: "Add more comments to this file, there aren't enough."
  expect_activate: no
  # The ask is about how many comments exist. This skill governs the register of
  # the comments that get written and never their number.
