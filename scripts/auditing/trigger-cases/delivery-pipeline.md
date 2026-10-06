# Trigger Cases: delivery-pipeline

## Positive (should activate)
- prompt: "A change request just landed. It reads like a small tweak but it touches the auth middleware — how much process does it actually deserve?"
  expect_activate: yes

- prompt: "I want you to stop and get my sign-off before you write any code, and again before anything gets committed."
  expect_activate: yes

- prompt: "Every fix, feature and refactor here follows a different improvised sequence. I want one phase order that scales up and down."
  expect_activate: yes

- prompt: "Last week you wrote a three-page plan for a typo fix and then edited a public interface with no plan at all. Fix that imbalance."
  expect_activate: yes

- prompt: "Take this spec and carry it all the way from request through to a commit, stopping where I need to weigh in."
  expect_activate: yes

- prompt: "We need rate limiting on the login endpoint, 5 attempts per minute per IP. Take it from design through to a commit, but check with me before you start implementing and again before you commit."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Please make the CSV export include a timestamp column. It's probably small, so use your judgment on how much planning it needs, but stop for my approval before coding and before the commit."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Take this requested refactor all the way to a commit, scaling the planning to the risk. Do not start implementation without my approval, and do not commit without asking me first."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "take this change to a commit ask before coding and committing"
  expect_activate: yes
  tags: [generated, off-register, gen:codex]

## Negative (should not activate)
- prompt: "Nobody will be around tonight to approve anything — this has to run start to finish unattended."
  expect_activate: no

- prompt: "How do I split this across four agents working at the same time without them overwriting each other's files?"
  expect_activate: no

- prompt: "I just want to read through the code and answer a question. Nothing here gets committed."
  expect_activate: no

- prompt: "Here's a pull request from an outside contributor. Go through it and tell me what's wrong with it."
  expect_activate: no

- prompt: "Squash my last 4 commits into one and rewrite the commit message to follow conventional commits. Don't change any code."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Plan out a multi-month migration from REST to GraphQL for the whole platform. I just want a roadmap with milestones, not an implementation."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Create a commit for the already-completed changes in the working tree, using the existing issue description as the commit message context."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Set up a pull-request template that requires human approval before coding and before merging commits."
  expect_activate: no
  tags: [generated, gen:codex]
