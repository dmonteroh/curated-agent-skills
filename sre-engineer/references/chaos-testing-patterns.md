# Chaos Testing Patterns

```python
import random
import time
from typing import Protocol

class ChaosInjector(Protocol):
    def inject(self) -> None:
        ...

    def rollback(self) -> None:
        ...

class LatencyInjector:
    def __init__(self, target_service: str, latency_ms: int):
        self.target_service = target_service
        self.latency_ms = latency_ms

    def inject(self) -> None:
        import subprocess
        subprocess.run([
            "tc", "qdisc", "add", "dev", "eth0",
            "root", "netem", "delay", f"{self.latency_ms}ms"
        ])

    def rollback(self) -> None:
        import subprocess
        subprocess.run(["tc", "qdisc", "del", "dev", "eth0", "root"])

class PodKiller:
    def __init__(self, namespace: str, label_selector: str, kill_percentage: float = 0.5):
        self.namespace = namespace
        self.label_selector = label_selector
        self.kill_percentage = kill_percentage
        self.killed_pods = []

    def inject(self) -> None:
        import subprocess
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", self.namespace,
             "-l", self.label_selector, "-o", "name"],
            capture_output=True,
            text=True
        )

        pods = result.stdout.strip().split('\n')
        num_to_kill = int(len(pods) * self.kill_percentage)
        pods_to_kill = random.sample(pods, num_to_kill)

        for pod in pods_to_kill:
            subprocess.run(["kubectl", "delete", pod, "-n", self.namespace])
            self.killed_pods.append(pod)

    def rollback(self) -> None:
        time.sleep(30)

class NetworkPartition:
    def __init__(self, source_pod: str, target_service: str):
        self.source_pod = source_pod
        self.target_service = target_service

    def inject(self) -> None:
        import subprocess
        subprocess.run([
            "kubectl", "exec", self.source_pod, "--",
            "iptables", "-A", "OUTPUT", "-d", self.target_service, "-j", "DROP"
        ])

    def rollback(self) -> None:
        import subprocess
        subprocess.run([
            "kubectl", "exec", self.source_pod, "--",
            "iptables", "-D", "OUTPUT", "-d", self.target_service, "-j", "DROP"
        ])
```

## Requirements

- Access to `kubectl`, `tc`, and `iptables` where relevant.
- Approved blast radius and rollback plans before running injections.

## Usage

1. Pick an injector and define the target scope.
2. Execute in staging or a limited blast radius first.
3. Record observations against the experiment hypothesis.

## Verification

- Confirm rollback restores normal traffic.
- Verify SLIs return to baseline after the test.
