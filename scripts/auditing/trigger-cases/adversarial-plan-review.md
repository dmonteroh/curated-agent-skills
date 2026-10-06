# Trigger Cases: adversarial-plan-review

## Positive (should activate)
- prompt: "We're about to run a one-way migration that rewrites every row in the users table. Here is the plan — I want it torn apart before we commit to it."
  expect_activate: yes

- prompt: "The team signed off on this API redesign in about ten minutes and nobody raised a single objection. That worries me more than it reassures me."
  expect_activate: yes

- prompt: "This whole architecture doc came out of one drafting pass and nothing in it has ever been contradicted. Can we stress it properly before we build?"
  expect_activate: yes

- prompt: "The proposal keeps trading coverage away for simplicity, and I want those tensions argued out in the open rather than smoothed over by one voice."
  expect_activate: yes

- prompt: "I need more than a verdict on this design — I need a written record of which objections it survived and why, for the decision log."
  expect_activate: yes

- prompt: "poke holes in my migration plan before i start"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Plan: I'm going to refactor the whole payments module in one big PR, with no feature flag, merge Monday, deploy Tuesday. Nothing's been written yet. Be adversarial. Try to find every way this goes wrong, then challenge your own objections and keep only the solid ones."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Before I greenlight the plan in docs/rollout-plan.md for moving us from monolith to microservices, I want a pre-mortem style attack on it. Pick it apart from multiple angles (cost, team capacity, data consistency, rollback), argue with yourself on each point, and report only the criticisms that survive."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Before we start implementation, stress-test this rollout plan: make the strongest case against it from technical, operational, and customer angles, then retain only the concerns that survive scrutiny."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "We still haven't agreed on what this feature is even supposed to do. Help me pin the goal down first."
  expect_activate: no

- prompt: "The migration approach is settled and signed off. Just help me write the first batch of the script."
  expect_activate: no

- prompt: "One open question: does this refactor break the existing test suite or not?"
  expect_activate: no

- prompt: "Can you write a step-by-step migration plan for moving our Postgres database to a sharded setup? We have about 2TB of data and want to key by tenant_id."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "I already shipped the sharding migration last week and it caused an outage. Can you write a postmortem that works out what went wrong and the contributing factors?"
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Play devil's advocate for a debate: argue that microservices are always better than monoliths. I'm not evaluating any plan of mine, I just want a persuasive speech."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Review the completed launch and write a retrospective explaining what went wrong and what we should change next time."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Can you proofread this plan for clarity, grammar, and missing sections before I send it to leadership?"
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Summarize the main risks listed in this project plan in a concise executive briefing."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
