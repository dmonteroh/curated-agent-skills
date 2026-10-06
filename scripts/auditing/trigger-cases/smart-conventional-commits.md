# Trigger Cases: smart-conventional-commits

## Positive (should activate)
- prompt: "Commit these changes with a good message."
  expect_activate: yes

- prompt: "Draft a conventional commit message for what I just changed — it adds an on-demand PDF download button."
  expect_activate: yes

- prompt: "Commit the unstaged changes; keep the message consistent with this repo's commit style."
  expect_activate: yes

- prompt: "commit this"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "I just added pagination to the users endpoint and bumped a dependency in package.json. Commit both, but separately, with good type(scope): summary messages."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I've finished the auth refactor and also fixed a typo in the README. Can you commit these as separate conventional commits, like feat(auth): ... and docs(readme): ...?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Turn the pending code changes into logically grouped commits with concise messages such as fix(api): handle empty responses."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Can you stage only the files that belong together and create clean conventional commits for the current code changes?"
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "Write a pull request description for this branch."
  expect_activate: no

- prompt: "Review the last five commits and tell me what changed."
  expect_activate: no

- prompt: "Squash and rewrite the history on main to clean it up."
  expect_activate: no

- prompt: "Can you set up commitlint and a husky hook so our repo enforces type(scope): summary commit messages?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Show me the git log for the last week and summarize what changed in each commit."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Undo my last commit but keep the changes in the working tree so I can redo it."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Push the existing local commits to the remote branch and open a pull request."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Create a release tag and generate release notes from the commits already on this branch."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Stash the current code changes so I can switch branches."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
