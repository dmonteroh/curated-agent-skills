# Trigger Cases: cli-tools

## Positive (should activate)

- prompt: "add a --dry-run flag to my cli"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Our `logsift` CLI currently only takes a file path as a positional argument. Can you add a `--since` flag that accepts durations like `30m` or `2h`, plus a `--format json|table` option, and update the --help output to match?"
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Our Rust CLI prints progress bars even when stdout is piped to a file, which makes the output garbage. Fix it so it detects a non-TTY, respects NO_COLOR, and add a `--quiet` flag."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Add shell completion generation to our Go cobra-based tool `kubectl-ctx`: a `completion` subcommand for bash, zsh, and fish, and document how to install each in the README."
  expect_activate: yes
  tags: [generated, gen:claude]

- prompt: "Redesign the CLI help text and error messages, add shell completion support, and ensure exit codes and color output behave consistently across supported operating systems."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Add a `doctor` command that checks installation and configuration, supports machine-readable output, and gives OS-specific remediation instructions."
  expect_activate: yes
  tags: [generated, gen:codex]

## Negative (should not activate)

- prompt: "How do I use the `find` command in Linux to locate files modified in the last 24 hours and delete them? I just want the one-liner for my terminal."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Can you explain what the flags `-xzvf` mean in `tar -xzvf archive.tar.gz`, and what the equivalent is on Windows PowerShell?"
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Write a React component for a settings page with a dark mode toggle and a form that saves user preferences to a REST API."
  expect_activate: no
  tags: [generated, gen:claude]

- prompt: "Update the README with examples of the existing commands, but do not change the program itself."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Build a desktop GUI for configuring the application’s settings, including a preferences window and platform-native menus."
  expect_activate: no
  tags: [generated, gen:codex]

- prompt: "Write a web dashboard that lets users run sync operations, view logs, and edit configuration through a browser."
  expect_activate: no
  tags: [generated, gen:codex]
