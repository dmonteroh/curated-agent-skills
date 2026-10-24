# Trigger Cases: changelog-automation

## Positive (should activate)

- prompt: "Can you set up our repo so that release notes get generated automatically from conventional commit messages whenever we tag a new version? We're on GitHub Actions."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Write a script that runs at release time, collects the titles of merged pull requests since the previous tag using the gh CLI, and writes them into the GitHub release body categorized by PR label."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "release notes from merged prs automatically"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Configure our CI to create a version-by-version list of changes from commit messages whenever we cut a release."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "When a release is published, generate the release notes and categorized changes from the PRs included in it."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Add a release-note generator that compiles merged PR titles into the GitHub release description."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Can you read through our existing CHANGELOG.md and fix the typos and inconsistent formatting in the entries for 2.x?"
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Summarize the last 20 commits in this repo for me so I can understand what changed this week."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Generate API documentation from source-code comments for each release."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Create release branches automatically when a pull request is merged."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Set up a GitHub Actions workflow that runs tests and lint on every pull request and blocks merging if they fail."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Build a dashboard showing all merged pull requests since the last release."
  expect_activate: no
  tags: [generated, gen:codex]
