# Trigger Cases: code-explain

## Positive (should activate)

- prompt: "explain how auth flow works in this repo"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "I just inherited this billing reconciliation module (src/billing/reconcile.py) and I can't follow it. Can you walk me through what it does step by step and why it's structured this way? I need to add support for partial refunds next week."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Here's a 300-line bash deploy script nobody on the team understands anymore. Walk me through what it does in order, what each trap and subshell is for, and what could go wrong, because I have to change the rollback logic."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Please trace how this React component gets its data, transforms it, and renders it. I need a detailed explanation of the reasoning behind the structure before I touch it."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Can you help me understand this legacy billing module from entry point to database write, step by step? Explain not only what it does but why it was designed this way."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "I need an onboarding-style walkthrough of this data pipeline code: inputs, intermediate state, outputs, and the purpose of the unusual logic, so I can take ownership of it."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Review my pull request diff for style problems and potential bugs, and give me a list of suggested changes."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Refactor the billing reconciliation module in src/billing/reconcile.py to split the giant function into smaller ones, keeping behavior identical."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Write documentation for our public REST API endpoints in the style of the existing docs, including request and response examples."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Fix the race condition in the job scheduler and add regression tests."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Refactor this module to remove duplication and make the API easier to use."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Write documentation for how to install, configure, and deploy this application."
  expect_activate: no
  tags: [generated, gen:codex]
