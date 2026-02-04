# DNS Failure Simulation

Provides host-based DNS blocking and latency configuration guidance.

## Prerequisites

- Root access on the target host.
- `dnsmasq` installed if using latency simulation.

## Usage

1. Apply the hosts-file block for the duration of the experiment.
2. Remove hosts entries during rollback.
3. Use dnsmasq latency config only in isolated environments.

## Verification

- Confirm DNS lookups for the target domain fail during the block.
- Validate name resolution returns after cleanup.

```python
import subprocess
import time
from contextlib import contextmanager

class DNSChaos:
    @staticmethod
    @contextmanager
    def block_domain(domain: str, duration_seconds: int = 60):
        try:
            subprocess.run([
                'sudo', 'sh', '-c',
                f'echo "127.0.0.1 {domain}" >> /etc/hosts'
            ], check=True)

            yield

        finally:
            time.sleep(duration_seconds)

            subprocess.run([
                'sudo', 'sed', '-i',
                f'/127.0.0.1 {domain}/d',
                '/etc/hosts'
            ], check=True)

    @staticmethod
    def add_dns_latency(domain: str, latency_ms: int):
        config = f"""
        # Add to /etc/dnsmasq.conf
        address=/{domain}/127.0.0.1
        min-cache-ttl=0
        """
        return config

with DNSChaos.block_domain('api.external-service.com', duration_seconds=120):
    print("DNS blocked - testing fallback behavior")
```
