# Trigger Cases: living-docs-governance

## Positive (should activate)
- prompt: "We've got a README, an architecture doc, a roadmap and an ADR folder and they all contradict each other. Can you sort out which one is supposed to own what?"
  expect_activate: yes

- prompt: "Every time someone picks this project back up they spend a day working out what's blocked and what's already been tried. How do we write that down so it stays true?"
  expect_activate: yes

- prompt: "We deleted the old parser months ago and it has been reintroduced twice since. Where should that decision live so it stops coming back?"
  expect_activate: yes

- prompt: "Our docs still describe the deploy script we removed last quarter. I don't want to adopt a docs platform, I just want them to stop rotting."
  expect_activate: yes

- prompt: "There's a wiki, a docs folder, and instructions in the repo root, and nobody knows which is authoritative. Can we give each one a clear job?"
  expect_activate: yes

- prompt: "This codebase is two years old and onboarding takes a week because nothing about health, ownership or where things live is written down consistently anywhere."
  expect_activate: yes

## Negative (should not activate)
- prompt: "My branch is code-complete — go through the docs and fix anything that no longer matches what I changed before I open the PR."
  expect_activate: no

- prompt: "There's no architecture document at all. Read the code and write one."
  expect_activate: no

- prompt: "Set up docs/context with the product, tech stack and workflow files and index them."
  expect_activate: no

- prompt: "It's a 40-line throwaway script I wrote this morning to rename some files. Does it need a docs structure?"
  expect_activate: no

- prompt: "Just explain what this function does."
  expect_activate: no
