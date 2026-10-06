# Trigger Cases: doc-generate

## Positive (should activate)
- prompt: "A new engineer starts Monday and this repo has no docs at all. What should they read on day one, and can you write it?"
  expect_activate: yes

- prompt: "Our AGENTS.md is stale and misses half our conventions. Refresh it from what's actually in the codebase."
  expect_activate: yes

- prompt: "Every time the assistant touches this old codebase it writes in its own style instead of ours. Work out the rules we actually follow here and write them down so that stops."
  expect_activate: yes

- prompt: "We captured our conventions three months ago and the codebase has moved on. Check what's changed since and update the rules file without throwing away the old decisions."
  expect_activate: yes

- prompt: "I just inherited this Flask service and there are no docs at all. Please read the code and write an architecture overview covering the main modules, how requests flow through them, and what external services it talks to."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Write a CONTRIBUTING-style 'getting started' guide for this monorepo. Look at the package.json scripts, the docker-compose file, and the CI config to figure out how to build, test, and run each service."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Create developer documentation for the existing codebase by inspecting its modules, package scripts, and deployment config; include an architecture overview and a runbook."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Please document this repo as it currently works. Read the implementation and config files, then produce setup instructions, component relationships, and API reference material."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "write a readme for this repo"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

## Negative (should not activate)
- prompt: "Go through this pull request and flag anywhere the author broke our naming conventions."
  expect_activate: no

- prompt: "Can you add a new POST /users/bulk endpoint to this Flask service that accepts a list of users and creates them in one transaction?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "The tests in tests/test_auth.py are failing with a KeyError. Can you debug it and fix the problem?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Write a unit test suite for the payment module that covers refunds, partial captures, and currency conversion edge cases."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Audit the repository for security vulnerabilities and produce a prioritized remediation plan."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Set up a CI pipeline that builds, tests, and deploys this application to staging."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Write a blog post announcing the 2.0 release of our library, aimed at developers who haven't used it yet. Cover the headline features and why they matter."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Summarize the repository’s recent commits into release notes for version 2.4."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
