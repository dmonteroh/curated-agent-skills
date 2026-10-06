# Trigger Cases: subagent-orchestrator

## Positive (should activate)
- prompt: "I have three independent failures in auth API, frontend rendering, and DB migration. Please partition work, assign disjoint claim sets by folder, dispatch workers, and verify only after all worker sessions end."
  expect_activate: yes

- prompt: "We need reviewer and implementer subagents for two separate modules, with strict allowed/forbidden paths and a controller-owned integration gate. Orchestrate this safely."
  expect_activate: yes

- prompt: "Two of these tasks both write to the staging database and one of them binds the local Redis port. Can they still run at the same time, and how do I carve that up?"
  expect_activate: yes

- prompt: "Each worker also pushes to its own deploy target and writes to a shared S3 bucket. I want the overlap ruled out before anything runs in parallel."
  expect_activate: yes

- prompt: "The reviewer keeps handing the same finding back to the implementer and we're on round four with no end in sight. How do I bound this so it either lands or comes back to me?"
  expect_activate: yes

- prompt: "split this refactor across parallel agents so they dont conflict"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "We're adding i18n across the whole monorepo: the web app, the mobile app, the shared UI library, and the email templates. Split this among parallel agents however makes sense and make sure their edits don't conflict when merged."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I need to ship a new billing system touching the API, database, UI, and tests. Figure out whether multiple coding agents should work in parallel and manage their boundaries so they do not overwrite each other."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Break down this monorepo migration for several AI helpers only if parallel work makes sense, then coordinate ownership of files and integration."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "Before I split any of this up, I just want to know whether the worker CLI is installed and logged in on this machine."
  expect_activate: no

- prompt: "The root cause is unknown and likely shared across services. First do one deep investigation and propose options."
  expect_activate: no

- prompt: "Fix the failing test in tests/test_auth.py, it looks like a token expiry comparison is off by one."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Write a Python script that runs a list of shell commands concurrently using a thread pool and collects their output."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Help me design a multi-agent architecture for my customer support chatbot, where one agent handles billing, another handles shipping, and a router picks between them."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Our team of five developers is working on the same repo and keeps getting merge conflicts. Can you suggest a branching strategy and code ownership rules?"
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Implement the payment-service refactor yourself from start to finish; do not delegate any portion of it."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Split this one large source file into smaller modules so the code is easier to maintain."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
