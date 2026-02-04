# Docker Container Chaos (Pumba)

Provides Pumba commands for container-level chaos.

## Prerequisites

- Docker daemon access on the target host.
- Pumba installed on the target host.

## Usage

1. Run a single Pumba command per experiment to isolate effects.
2. Use short durations and verify rollback behavior.

## Verification

- Confirm containers are restarted or unpaused after the command completes.
- Validate service steady state returns to baseline.

```bash
#!/bin/bash

pumba --interval 30s kill --signal SIGKILL "re2:^myapp"

pumba pause --duration 15s myapp-container

pumba netem \
  --duration 5m \
  --interface eth0 \
  delay \
    --time 300 \
    --jitter 50 \
  myapp-container

pumba netem \
  --duration 5m \
  loss \
    --percent 20 \
  myapp-container

pumba netem \
  --duration 5m \
  rate \
    --rate 1mbit \
  myapp-container

pumba stop --duration 2m "re2:^production-.*"
```
