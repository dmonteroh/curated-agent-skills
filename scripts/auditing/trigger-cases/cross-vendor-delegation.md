# Trigger Cases: cross-vendor-delegation

## Positive (should activate)
- prompt: "I want a genuinely independent second opinion on this design from a model that isn't the one that drafted it."
  expect_activate: yes

- prompt: "The other model lives behind its own CLI with no shared working directory. How do I hand it a bounded task and get a usable answer back?"
  expect_activate: yes

- prompt: "The outside reviewer's verdict decides whether we merge, so a hang or an empty response must not come back looking like approval."
  expect_activate: yes

- prompt: "What needs reviewing is a third-party PR body plus its diff — content I didn't write. Sending that straight into another agent's prompt makes me nervous."
  expect_activate: yes

- prompt: "Last time we shelled out to the other vendor's agent it returned nothing at all and we never worked out why."
  expect_activate: yes

## Negative (should not activate)
- prompt: "I want to fan this refactor out across four workers inside my own agent and merge their results."
  expect_activate: no

- prompt: "I want the outside model to actually make the edits and push a branch, not just give me an opinion."
  expect_activate: no

- prompt: "Does this build pass on Node 22 or not?"
  expect_activate: no

- prompt: "Should I sanity-check this against the same model family through a different API endpoint?"
  expect_activate: no
