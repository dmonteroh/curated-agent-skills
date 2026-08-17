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

## Negative (should not activate)
- prompt: "This runs as a systemd unit already — I want to set its restart policy and health check."
  expect_activate: no

- prompt: "I need to design the subcommand layout and how flags override the config file for this tool."
  expect_activate: no

- prompt: "The command shells out to ffmpeg, waits for it to finish, and exits with its status."
  expect_activate: no

- prompt: "We need rolling deploys and health checks across thirty replicas behind a load balancer."
  expect_activate: no
