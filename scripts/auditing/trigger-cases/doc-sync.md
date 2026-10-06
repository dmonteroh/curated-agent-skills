# Trigger Cases: doc-sync

## Positive (should activate)
- prompt: "The branch is code-complete and I'm about to open the PR. Make sure the docs actually match what shipped."
  expect_activate: yes

- prompt: "This change renamed two exported functions and moved a module. There are pages all over the repo still describing the old shape."
  expect_activate: yes

- prompt: "There's already a changelog entry on this branch. Check it against the diff and tighten it, but don't rewrite it out from under me."
  expect_activate: yes

- prompt: "Someone bumped the version file earlier on this branch. Does that bump still cover everything the branch ended up containing?"
  expect_activate: yes

- prompt: "The change touched two of the services named in our architecture diagram, and I want to know if the diagram is now wrong."
  expect_activate: yes

- prompt: "I'm about to merge my feature/auth-refactor branch. Can you go through the README and the docs folder and fix anything that no longer matches what I changed in the code?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "This branch changes the REST API response shapes in src/api. Please sweep the markdown docs and API reference and correct any examples or descriptions that are now wrong before we merge."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Before approving the merge, reconcile the docs with the changed code and correct any outdated descriptions or usage instructions."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Do a documentation pass for this PR: find references made inaccurate by the branch changes and bring them up to date."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "docs are stale after my changes fix them before merge"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

## Negative (should not activate)
- prompt: "We have no documentation at all. Write the getting-started guide from the code."
  expect_activate: no

- prompt: "Nothing is in flight right now — I just want a general freshness sweep over the docs folder."
  expect_activate: no

- prompt: "There's no changelog entry for this work yet. Write one from the commits."
  expect_activate: no

- prompt: "This shipped last week. Draft the upgrade guide and the announcement post."
  expect_activate: no

- prompt: "Can you review the code changes on my branch for bugs and style problems before I merge?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Add docstrings to all the public functions in src/utils that don't have them yet."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Fix the typos and awkward grammar in the README. The code hasn't changed, I just want the prose cleaned up."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Write the PR description for my branch, summarizing what changed and why."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Resolve the merge conflicts between my branch and main in the docs folder, keeping both sets of edits."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Add documentation for the new feature introduced in this branch, including a new getting-started guide."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Update the project’s documentation site theme and navigation structure."
  expect_activate: no
  tags: [generated, gen:codex]
