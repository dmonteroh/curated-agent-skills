# Trigger Cases: pr-description

## Positive (should activate)
- prompt: "Draft the PR description for this branch — the task brief is in docs/briefs/checklist-export.md."
  expect_activate: yes

- prompt: "Write a pull request body for my feature branch against develop."
  expect_activate: yes

- prompt: "The description on this PR is stale after the latest commits; refresh it."
  expect_activate: yes

- prompt: "pr body pls with test steps"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "I finished the retry-logic refactor on this branch. Can you put together the text for the PR, with what changed, why, and how someone can try it locally?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Write up a PR description based on the diff against main. Reviewers should know the motivation and be able to click through and test it themselves."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Prepare the text for a PR on the current branch, with a concise summary, rationale, and reviewer-facing hand-test instructions."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Can you draft the PR body for this branch? Cover what changed, why it was needed, and how someone can verify it manually."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "Write a commit message for these staged changes."
  expect_activate: no

- prompt: "Create the pull request on GitHub and merge it once CI is green."
  expect_activate: no

- prompt: "Summarize the diff file by file so I can review it."
  expect_activate: no

- prompt: "Reply to the reviewer comments on my open PR; they asked why I used a mutex instead of a channel. Draft a response."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Summarize the open pull request #482 for me so I can understand what it does before I review it."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Draft release notes explaining what changed in this branch and why."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Review the current branch and leave inline code-review comments on any issues you find."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Add unit tests covering the new retry logic on this branch."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Update the project’s CONTRIBUTING guide with instructions for manually testing changes before submitting a PR."
  expect_activate: no
  tags: [generated, gen:codex]
