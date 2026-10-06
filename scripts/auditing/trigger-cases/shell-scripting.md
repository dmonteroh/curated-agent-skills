# Trigger Cases: shell-scripting

## Positive (should activate)
- prompt: "Write a bash script that rotates log files older than 7 days in /var/log/myapp."
  expect_activate: yes

- prompt: "Our CI needs a shell script to build and tag the Docker image; make it safe and portable."
  expect_activate: yes

- prompt: "My script dies with 'unbound variable' under set -u but only in the container — help me fix it."
  expect_activate: yes

- prompt: "Review this install.sh for quoting and portability problems before we ship it."
  expect_activate: yes

- prompt: "My deploy script shells out to curl, git and helm. How do I write tests for it without actually hitting any of those?"
  expect_activate: yes

- prompt: "How do I cover the failure branches in this bash wrapper when every branch depends on what the package manager returns?"
  expect_activate: yes

- prompt: "bash script to batch rename files with spaces in them"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "I have a deploy script that keeps breaking when someone's path has a space or when a command fails halfway through. Can you rewrite it so it's properly quoted, exits on errors, cleans up temp files with a trap, and works on any machine without hardcoded paths? I'll paste it below: cd $APP_DIR && git pull && cp -r build/* $DEST && systemctl restart app"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Automate log archival with Bash: make it work from any checkout location, use safe filename handling, and stop with useful errors."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)
- prompt: "Write a Python script that parses this JSON file and posts the results to an API."
  expect_activate: no

- prompt: "Help me configure nginx as a reverse proxy for two services."
  expect_activate: no

- prompt: "Build an interactive terminal UI with panels and live updating graphs."
  expect_activate: no

- prompt: "Help me write a PowerShell script that backs up my Documents folder to a network share on Windows every night."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Write a GitHub Actions workflow YAML that runs my test suite on push and uploads coverage to Codecov."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "What's the best way to learn bash scripting? Can you recommend some books or tutorials for a beginner?"
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Can you write a Makefile that builds my C project, with targets for debug and release builds and a clean target?"
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Write a Python program that watches a folder and uploads new files to cloud storage."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Create an Ansible playbook to install and configure our backup service on Linux hosts."
  expect_activate: no
  tags: [generated, gen:codex]
