# Trigger Cases: pre-publication-sanitization

## Positive (should activate)
- prompt: "We're flipping this repo from private to public on Friday. What has to be cleared out of it first, including the history?"
  expect_activate: yes

- prompt: "I want to carve a demo project out of our internal codebase and publish it alongside a blog post."
  expect_activate: yes

- prompt: "This repo is already public but empty. We're about to push two years of code that was developed behind the firewall."
  expect_activate: yes

- prompt: "Another team wants to open-source their service and they need my approval before it goes out. What do I check?"
  expect_activate: yes

- prompt: "The sweep turned up an internal hostname buried in an old commit. Does that block the release, and who gets to decide?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "The repo has been public for a year and I just spotted an internal URL in the README."
  expect_activate: no

- prompt: "We're transferring the repo to a different org inside the same company. It stays private either way."
  expect_activate: no

- prompt: "Add a LICENSE, a contributing guide and issue templates before we announce this."
  expect_activate: no

- prompt: "Where should our production secrets actually live, and how often should they rotate?"
  expect_activate: no
