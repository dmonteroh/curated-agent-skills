# Server Resource Exhaustion

Provides stress-ng and iperf3 examples for resource exhaustion.

## Prerequisites

- Packages installed: `stress-ng`, `iperf3`.
- Access to the target host with appropriate privileges.

## Usage

1. Run CPU, memory, or disk stressors one at a time.
2. Use iperf3 to saturate network bandwidth in a controlled window.
3. Stop the process when guardrails breach.

## Verification

- Confirm resource metrics reach the intended thresholds.
- Validate services recover to steady state after stopping the stressor.

```bash
#!/bin/bash

sudo apt-get install -y stress-ng iperf3

stress-ng --cpu $(nproc --all) --cpu-load 80 --timeout 5m

TOTAL_MEM_MB=$(free -m | awk 'NR==2{print $2}')
STRESS_MEM_MB=$((TOTAL_MEM_MB * 70 / 100))
stress-ng --vm 1 --vm-bytes ${STRESS_MEM_MB}M --timeout 5m

stress-ng --hdd 4 --hdd-bytes 1G --timeout 5m

iperf3 -c target-server -t 300 -P 10
```
