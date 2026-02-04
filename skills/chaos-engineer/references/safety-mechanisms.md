# Safety Mechanisms

Provides an example safety wrapper for chaos experiment execution.

## Usage

1. Populate `config` with steady-state metrics and blast radius limits.
2. Integrate the safety wrapper around the chaos execution function.
3. Ensure rollback logic is implemented in the wrapper.

## Verification

- Trigger a manual kill switch and confirm rollback executes.
- Validate the monitor detects guardrail breaches.
- Confirm the wrapper exits once recovery completes.

```python
import asyncio
from typing import Callable

class ChaosExperimentSafety:
    def __init__(self, config: dict):
        self.config = config
        self.kill_switch_active = False
        self.metrics = {}

    async def run_with_safety(self, chaos_fn: Callable):
        if not await self.verify_steady_state():
            raise Exception("System not in steady state - aborting")

        rollback_task = asyncio.create_task(self.monitor_for_rollback())
        chaos_task = asyncio.create_task(chaos_fn())

        try:
            done, pending = await asyncio.wait(
                [chaos_task, rollback_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            if rollback_task in done:
                chaos_task.cancel()
                await self.rollback()

        finally:
            await self.ensure_system_recovery()

    async def verify_steady_state(self) -> bool:
        for metric in self.config['steady_state']['metrics']:
            value = await self.query_metric(metric['query'])
            if not self.within_threshold(value, metric['threshold']):
                return False
        return True

    async def monitor_for_rollback(self):
        start_time = asyncio.get_event_loop().time()

        while True:
            if asyncio.get_event_loop().time() - start_time > \
               self.config['blast_radius']['duration_seconds']:
                return "duration_exceeded"

            if self.kill_switch_active:
                return "manual_kill_switch"

            error_rate = await self.query_metric("error_rate")
            if error_rate > float(self.config['blast_radius']['max_error_rate'].strip('%')):
                return "error_rate_exceeded"

            await asyncio.sleep(5)
```
