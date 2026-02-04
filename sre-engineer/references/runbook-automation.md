# Runbook Automation

Convert manual runbooks to automated scripts.

```python
from typing import List, Tuple
from dataclasses import dataclass
import subprocess

@dataclass
class RunbookStep:
    description: str
    command: str
    critical: bool = True
    verify: str | None = None

class AutomatedRunbook:
    """Execute runbook steps automatically."""

    def __init__(self, name: str):
        self.name = name
        self.steps: List[RunbookStep] = []

    def add_step(self, step: RunbookStep):
        self.steps.append(step)

    def execute(self, dry_run: bool = False) -> Tuple[bool, List[str]]:
        outputs = []

        for i, step in enumerate(self.steps, 1):
            outputs.append(f"\n[Step {i}/{len(self.steps)}] {step.description}")

            if dry_run:
                outputs.append(f"Would run: {step.command}")
                continue

            try:
                result = subprocess.run(
                    step.command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if result.returncode != 0:
                    outputs.append(f"ERROR: {result.stderr}")
                    if step.critical:
                        return False, outputs
                else:
                    outputs.append(result.stdout)

                if step.verify:
                    verify_result = subprocess.run(
                        step.verify,
                        shell=True,
                        capture_output=True,
                        text=True,
                    )
                    if verify_result.returncode != 0:
                        outputs.append(f"VERIFICATION FAILED: {verify_result.stderr}")
                        if step.critical:
                            return False, outputs

            except subprocess.TimeoutExpired:
                outputs.append("ERROR: Command timed out")
                if step.critical:
                    return False, outputs

        return True, outputs

failover_runbook = AutomatedRunbook("Database Failover")

failover_runbook.add_step(RunbookStep(
    description="Stop writes to primary database",
    command="kubectl exec -it postgres-primary-0 -- psql -c 'ALTER SYSTEM SET default_transaction_read_only = on;'",
    critical=True,
))

failover_runbook.add_step(RunbookStep(
    description="Wait for replication lag to clear",
    command="sleep 10",
    critical=False,
))

failover_runbook.add_step(RunbookStep(
    description="Promote replica to primary",
    command="kubectl exec -it postgres-replica-0 -- pg_ctl promote",
    critical=True,
    verify="kubectl exec -it postgres-replica-0 -- psql -c 'SELECT pg_is_in_recovery();' | grep -q 'f'",
))

failover_runbook.add_step(RunbookStep(
    description="Update service to point to new primary",
    command="kubectl patch service postgres -p '{\"spec\":{\"selector\":{\"role\":\"replica\"}}}'",
    critical=True,
))

success, output = failover_runbook.execute(dry_run=False)
print('\n'.join(output))
```

## Requirements

- Access to `kubectl`, `psql`, and the service cluster.
- Commands must be tested in a staging environment before production.

## Usage

1. Replace commands with service-specific runbook steps.
2. Run with `dry_run=True` to review commands.
3. Execute with `dry_run=False` during approved maintenance windows.

## Verification

- Ensure each step's `verify` command succeeds.
- Confirm the service is healthy and traffic routes to the new primary.
