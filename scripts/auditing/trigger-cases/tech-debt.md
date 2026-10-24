# Trigger Cases: tech-debt

## Positive (should activate)

- prompt: "whats rotting in this codebase rank it and plan the fixes"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "We've been shipping fast for two years and the repo is a mess. Can you audit it for tech debt, rank the worst offenders by how much they slow us down, and give me a prioritized cleanup plan?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I'm taking over this service from a departed teammate. Before I touch anything, I want an inventory of the technical debt here, sorted by severity, with a phased plan for paying it down."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Our team gets one sprint per quarter for debt reduction. Look through the repo, figure out which shortcuts and rotting areas are costing us the most, and propose what we should tackle first and why."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Review our repository for accumulated code rot—duplication, fragile dependencies, outdated patterns, and missing tests—then rank the risks and turn the findings into an actionable remediation roadmap."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Perform a technical-debt review: find the rot, assess its impact on reliability and developer velocity, and lay out a practical cleanup sequence with milestones."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Write a migration guide for upgrading this project from React 17 to React 18, with the steps in order."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Can you review my pull request diff for bugs and style problems before I merge it?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Run a security audit of this codebase and list any vulnerabilities by severity, with fixes for the critical ones."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Pay down the debt in utils/date.js by rewriting those hacky helpers cleanly right now. I already know what's wrong with them."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Find all the TODO comments in the repo and print them as a list with file and line number. I don't need any ranking or plan."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Migrate the application from PostgreSQL 13 to PostgreSQL 16 with minimal downtime."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Investigate why the production checkout endpoint is timing out and fix the immediate cause."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Refactor the payment module to use the repository pattern."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
