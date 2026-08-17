# Trigger Cases: code-review

## Positive (should activate)
- prompt: "I need help with this: Reviewing pull requests, diffs, or local changes. Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Establishing code review standards for a team. Can you guide me?"
  expect_activate: yes

- prompt: "An agent rewrote 40 files to use our new logging helper. The lines it touched look fine — I'm worried about the ones it quietly skipped."
  expect_activate: yes

- prompt: "This PR is a codemod across the whole repo. How do I check nothing got dropped along the way rather than just reading the changed lines?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: There are no code changes to review. No planning, just implementation."
  expect_activate: no

- prompt: "Set up something that hard-blocks the merge button whenever it finds anything, no exceptions."
  expect_activate: no
