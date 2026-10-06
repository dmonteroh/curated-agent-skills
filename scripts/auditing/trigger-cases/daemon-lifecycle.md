# Trigger Cases: daemon-lifecycle

## Positive (should activate)
- prompt: "I want our CLI to keep a warm background process alive between invocations so it stops paying cold-start cost every time. No systemd, no containers."
  expect_activate: yes

- prompt: "Running two commands at once spawns two copies of our background server and they fight over the same port."
  expect_activate: yes

- prompt: "The tool signaled a PID out of its own state file after a reboot and killed something completely unrelated."
  expect_activate: yes

- prompt: "The helper process should shut itself down after fifteen idle minutes and handle SIGTERM without leaving orphans behind."
  expect_activate: yes

- prompt: "Separate invocations need to find the already-running worker and attach to it instead of starting another one."
  expect_activate: yes

- prompt: "make my cli start a background daemon on demand and quit when idle"
  expect_activate: yes
  tags: [generated, off-register, gen:claude]

- prompt: "Implement an on-demand helper process for the command-line client. It should use a PID/socket lock so concurrent invocations share one instance, and it should terminate itself after an idle timeout."
  expect_activate: yes
  tags: [generated, gen:codex]

- prompt: "Our Node CLI spends forever booting a language service. Make it so the first run forks a detached background process, later runs talk to that one process, and it exits on its own after 15 idle minutes. Make sure two CLI invocations racing at startup don't spawn two daemons."
  expect_activate: yes
  tags: [generated, gen:claude]

## Negative (should not activate)
- prompt: "This runs as a systemd unit already — I want to set its restart policy and health check."
  expect_activate: no

- prompt: "I need to design the subcommand layout and how flags override the config file for this tool."
  expect_activate: no

- prompt: "The command shells out to ffmpeg, waits for it to finish, and exits with its status."
  expect_activate: no

- prompt: "We need rolling deploys and health checks across thirty replicas behind a load balancer."
  expect_activate: no

- prompt: "Have each CLI command start a temporary helper subprocess, perform one operation, and always terminate it before the command exits."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Write a long-running HTTP server in Rust with graceful shutdown on SIGTERM; it should be installed and managed by launchd on macOS."
  expect_activate: no
  tags: [generated, near-miss, gen:claude]

- prompt: "Create a persistent cache file so future CLI runs are faster, with no background process involved."
  expect_activate: no
  tags: [generated, near-miss, gen:codex]

- prompt: "Help me write a cron job that runs my cleanup script every night at 2am and emails me if it fails."
  expect_activate: no
  tags: [generated, gen:claude]
