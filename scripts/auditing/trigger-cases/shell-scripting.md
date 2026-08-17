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

## Negative (should not activate)
- prompt: "Write a Python script that parses this JSON file and posts the results to an API."
  expect_activate: no

- prompt: "Help me configure nginx as a reverse proxy for two services."
  expect_activate: no

- prompt: "Build an interactive terminal UI with panels and live updating graphs."
  expect_activate: no
