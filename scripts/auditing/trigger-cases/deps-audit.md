# Trigger Cases: deps-audit

## Positive (should activate)

- prompt: "Can you audit our dependencies in this repo? I need to know which packages have known CVEs, which are out of date, and whether any have licenses that would be a problem for us shipping commercially. Give me a prioritized list of what to upgrade."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Please scan the Maven dependencies in our pom.xml for CVEs and end-of-life versions, flag any AGPL or other copyleft licenses, and summarize which ones we should upgrade first."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Before we cut the release, can you check all third-party libraries in this project for security advisories, how far behind latest they are, and license compatibility with MIT? I want a concrete upgrade list."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "check deps for vulnerabilities and what to upgrade"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Review our package manifests and lockfiles for vulnerable or outdated libraries and flag any license compliance issues."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Identify third-party packages we should update because of vulnerabilities, end-of-life status, or problematic licenses."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Check every direct and transitive dependency for CVEs, outdated releases, and license risks; list the safest versions to move to."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "Can you write a function in this repo that parses a requirements.txt file and returns a dict of package names to pinned versions?"
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Review the authentication code in src/auth for security bugs like SQL injection, weak hashing, or missing input validation."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Can you explain what a CVE is and how severity scores like CVSS are calculated?"
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Help me choose a license for my own open source project. I'm deciding between MIT and Apache 2.0."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Why does npm install keep failing with a peer dependency conflict between eslint and typescript-eslint? Help me resolve it."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Compare the runtime performance of our current database driver against alternative libraries."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Check whether our project supports the latest Node.js and Python versions, and update our CI matrix if needed."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]
