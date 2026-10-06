# Trigger Cases: code-review

## Positive (should activate)
- prompt: "An agent rewrote 40 files to use our new logging helper. The lines it touched look fine — I'm worried about the ones it quietly skipped."
  expect_activate: yes

- prompt: "This PR is a codemod across the whole repo. How do I check nothing got dropped along the way rather than just reading the changed lines?"
  expect_activate: yes

- prompt: "go through the bot comments on my pr"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Can you review my PR before I merge it? It changes the session token refresh logic in auth/session.py and I'm worried about race conditions or anything insecure."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Please do a pre-merge code review of this diff for edge cases, unsafe input handling, slow paths, and maintainability concerns."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Audit the proposed refactor like a senior reviewer: look for bugs, race conditions, security holes, and style issues before I approve it."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "Set up something that hard-blocks the merge button whenever it finds anything, no exceptions."
  expect_activate: no

- prompt: "Please resolve the merge conflicts in my branch against main and then push it."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Can you write a PR description for my changes to the session token refresh logic? Summarize what changed and why."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Review the product requirements document for missing user stories and unclear acceptance criteria."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Look over this incident postmortem and point out gaps in the timeline or root-cause analysis."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Optimize the reporting query so the dashboard loads in under one second."
  expect_activate: no
  tags: [generated, gen:codex]
