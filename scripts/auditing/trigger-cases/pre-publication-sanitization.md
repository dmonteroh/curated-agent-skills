# Trigger Cases: pre-publication-sanitization

## Positive (should activate)
- prompt: "We're flipping this repo from private to public on Friday. What has to be cleared out of it first, including the history?"
  expect_activate: yes

- prompt: "I want to carve a demo project out of our internal codebase and publish it alongside a blog post."
  expect_activate: yes

- prompt: "This repo is already public but empty. We're about to push two years of code that was developed behind the firewall."
  expect_activate: yes

- prompt: "Another team wants to open-source their service and they need my approval before it goes out. What do I check?"
  expect_activate: yes

- prompt: "The sweep turned up an internal hostname buried in an old commit. Does that block the release, and who gets to decide?"
  expect_activate: yes

- prompt: "scrub git history before public release"
  expect_activate: yes
  tags: [generated, off-register, gen:codex]

- prompt: "This repo has 4 years of history and was always private. We want to publish it on GitHub. Help me sanitize it end to end: secrets, internal package registry URLs, TODO comments naming coworkers, and old config files with production IPs. History included, not just the current tree."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Please sanitize this repository and all branches/tags before open-sourcing it; remove internal hostnames, private package registries, names, and any leaked tokens from historical commits."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "The repo has been public for a year and I just spotted an internal URL in the README."
  expect_activate: no

- prompt: "We're transferring the repo to a different org inside the same company. It stays private either way."
  expect_activate: no

- prompt: "Add a LICENSE, a contributing guide and issue templates before we announce this."
  expect_activate: no

- prompt: "Where should our production secrets actually live, and how often should they rotate?"
  expect_activate: no

- prompt: "Can you scan my working directory for hardcoded passwords and move them into environment variables? The repo is staying private, and I don't care about history."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Remove the large binary files accidentally committed to our repo's history with git-filter-repo so the clone size shrinks. Nothing sensitive, just bloat."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "I'm making our public repo private again. What settings should I change on GitHub, and what happens to forks and stars?"
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Can you set up a pre-commit hook with gitleaks so developers on our private repo can't accidentally commit secrets going forward?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Remove obsolete secrets from the current deployment configuration and rotate the affected credentials; the repository will remain private."
  expect_activate: no
  tags: [generated, gen:codex]
