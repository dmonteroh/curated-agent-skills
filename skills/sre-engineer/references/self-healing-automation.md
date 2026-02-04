# Self-Healing Automation

Automate common failure remediation with safe retries and escalation.

```python
import subprocess
import logging
from typing import Callable, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class HealthCheck:
    name: str
    check: Callable[[], bool]
    remediate: Callable[[], bool]
    max_retries: int = 3

class SelfHealer:
    """Automatically remediate common failures."""

    def __init__(self):
        self.health_checks: Dict[str, HealthCheck] = {}

    def register(self, check: HealthCheck):
        self.health_checks[check.name] = check

    def run(self):
        for check in self.health_checks.values():
            if not check.check():
                logger.warning(f"Health check failed: {check.name}")
                self._remediate(check)

    def _remediate(self, check: HealthCheck):
        for attempt in range(check.max_retries):
            logger.info(f"Remediation attempt {attempt + 1}/{check.max_retries}")
            if check.remediate() and check.check():
                logger.info(f"Health check passed after remediation: {check.name}")
                return
        logger.error(f"Remediation failed after {check.max_retries} attempts")
        self._escalate(check)

    def _escalate(self, check: HealthCheck):
        logger.error(f"ESCALATING: {check.name} - auto-remediation failed")

def check_disk_space() -> bool:
    result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    if len(lines) > 1:
        fields = lines[1].split()
        use_percent = int(fields[4].rstrip('%'))
        return use_percent < 80
    return True

def cleanup_disk() -> bool:
    try:
        subprocess.run(
            ["find", "/var/log", "-name", "*.log", "-mtime", "+7", "-delete"],
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def check_service_responsive() -> bool:
    try:
        result = subprocess.run(
            ["curl", "-f", "http://localhost:8080/health"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False

def restart_service() -> bool:
    try:
        subprocess.run(["systemctl", "restart", "myservice"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

healer = SelfHealer()
healer.register(HealthCheck(
    name="disk_space",
    check=check_disk_space,
    remediate=cleanup_disk,
))
healer.register(HealthCheck(
    name="service_health",
    check=check_service_responsive,
    remediate=restart_service,
))

if __name__ == "__main__":
    healer.run()
```

## Requirements

- Local access to `df`, `find`, `curl`, and `systemctl` equivalents.
- Health endpoints reachable from the host running the script.

## Usage

1. Update health checks and remediation functions for the target service.
2. Save as `self_healing.py` and run `python self_healing.py`.
3. Review logs for remediation actions and escalation.

## Verification

- Trigger a known failure (disk fill or service stop).
- Confirm the remediation runs and the health check passes afterward.
