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

## Negative (should not activate)
- prompt: "Implement this exact feature now; requirements are final and no design/exploration is needed."
  expect_activate: no

- prompt: "Before I split any of this up, I just want to know whether the worker CLI is installed and logged in on this machine."
  expect_activate: no

- prompt: "The root cause is unknown and likely shared across services. First do one deep investigation and propose options."
  expect_activate: no
