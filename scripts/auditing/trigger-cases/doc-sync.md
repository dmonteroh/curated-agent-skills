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

## Negative (should not activate)
- prompt: "We have no documentation at all. Write the getting-started guide from the code."
  expect_activate: no

- prompt: "Nothing is in flight right now — I just want a general freshness sweep over the docs folder."
  expect_activate: no

- prompt: "There's no changelog entry for this work yet. Write one from the commits."
  expect_activate: no

- prompt: "This shipped last week. Draft the upgrade guide and the announcement post."
  expect_activate: no
