# Trigger Cases: git-workflow

## Positive (should activate)
- prompt: "When did this feature-flag check get removed, and who took it out? I want the commit, not a guess."
  expect_activate: yes

- prompt: "Don't change anything — just tell me where this repo stands: current branch, what's staged, how far ahead of origin we are."
  expect_activate: yes

- prompt: "I was rebasing my feature branch onto main and hit a bunch of conflicts in package-lock.json and src/api/client.ts. I'm halfway through and git status says \"rebase in progress\". Can you help me get through it without losing my changes?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I need to pull just two commits from my colleague's branch `hotfix/payment-timeout` into release-2.3 without bringing over the rest. Can you cherry-pick them and deal with any conflicts?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I rebased my PR branch locally and now git push is rejected because the histories diverged. Can you walk me through force-pushing safely so I don't clobber anyone else's commits on the remote?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "I accidentally reset hard and lost two commits from yesterday—please recover them from reflog and restore the branch safely."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "My PR branch diverged after a merge; clean up the history with an interactive rebase and squash the fixup commits."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "lost my commits after reset hard how to get back"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

## Negative (should not activate)

- prompt: "Set up a GitHub Actions workflow that runs lint and tests on every pull request to main."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Can you write a Python script that parses a file with conflict markers like <<<<<<< and ======= and reports how many conflicts are in each file? It's for a lint tool, I'm not resolving anything right now."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Can you recover a deleted file from my laptop? I removed report.docx from the trash and it was never in version control."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Rebase the database indexes overnight so the reporting queries run faster."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Resolve the conflicting edits in this Word document and combine both authors’ changes."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Recover the deleted customer records from last night’s production backup."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
