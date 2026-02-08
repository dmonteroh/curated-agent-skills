# Trigger Cases: cli-tools

## Positive (should activate)
- prompt: "I need help with this: Designing a CLI command surface (subcommands/flags/args). Can you guide me?"
  expect_activate: yes

- prompt: "I need help with this: Implementing argument parsing and validation. Can you guide me?"
  expect_activate: yes

## Negative (should not activate)
- prompt: "Please do this exactly now: The task is not a CLI/terminal tool. No planning, just implementation."
  expect_activate: no
