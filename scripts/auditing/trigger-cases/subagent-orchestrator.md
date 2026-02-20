# Trigger Cases: subagent-orchestrator

## Positive (should activate)
- prompt: "I have three independent failures in auth API, frontend rendering, and DB migration. Please partition work, assign disjoint claim sets by folder, dispatch workers, and verify only after all worker sessions end."
  expect_activate: yes

- prompt: "We need reviewer and implementer subagents for two separate modules, with strict allowed/forbidden paths and a controller-owned integration gate. Orchestrate this safely."
  expect_activate: yes

## Negative (should not activate)
- prompt: "Implement this exact feature now; requirements are final and no design/exploration is needed."
  expect_activate: no

- prompt: "The root cause is unknown and likely shared across services. First do one deep investigation and propose options."
  expect_activate: no
