# SLO Calculations

## Error Budget Math

```python
from datetime import timedelta
from typing import NamedTuple

class SLOTarget(NamedTuple):
    target: float
    window: timedelta

    @property
    def error_budget(self) -> float:
        return 1 - self.target

    @property
    def allowed_downtime(self) -> timedelta:
        total_seconds = self.window.total_seconds()
        allowed_seconds = total_seconds * self.error_budget
        return timedelta(seconds=allowed_seconds)
```

## Multi-Window SLO Tracking

```python
from datetime import timedelta

class MultiWindowSLO:
    """Track SLO compliance across multiple time windows."""

    def __init__(self, target: float):
        self.target = target
        self.windows = {
            '1h': timedelta(hours=1),
            '24h': timedelta(hours=24),
            '7d': timedelta(days=7),
            '30d': timedelta(days=30),
        }

    def check_compliance(self, sli_values: dict[str, float]) -> dict[str, bool]:
        return {window: sli >= self.target for window, sli in sli_values.items()}

    def get_burn_rate(self, current_sli: float) -> float:
        error_budget = 1 - self.target
        current_error_rate = 1 - current_sli
        if error_budget == 0:
            return float('inf')
        return current_error_rate / error_budget
```
