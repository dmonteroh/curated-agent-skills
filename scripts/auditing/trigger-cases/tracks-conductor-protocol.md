# Trigger Cases: tracks-conductor-protocol

## Positive (should activate)
- prompt: "I need help with this: Needing to intake work, formalize it into task briefs, group it into tracks, plan it, and execute it. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Requiring an indexing/registry system (like ADR indexes) that stays deterministic across contributors. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The request is a single small code change with no need for tracking or planning artifacts. No planning, just implementation."
  expect_activate: no
