# Error Budget Fundamentals

Error budget = 1 - SLO target. It represents acceptable unreliability.

```python
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum

class BudgetStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    EXHAUSTED = "exhausted"

@dataclass
class ErrorBudget:
    """Error budget tracker."""
    slo_target: float
    window_days: int

    @property
    def budget_percentage(self) -> float:
        return (1 - self.slo_target) * 100

    @property
    def allowed_downtime(self) -> timedelta:
        total_minutes = self.window_days * 24 * 60
        error_minutes = total_minutes * (1 - self.slo_target)
        return timedelta(minutes=error_minutes)

    def remaining_budget(self, actual_sli: float) -> float:
        budget_used = 1 - actual_sli
        total_budget = 1 - self.slo_target
        if total_budget == 0:
            return 0.0
        return max(0.0, 1 - (budget_used / total_budget))

    def get_status(self, actual_sli: float) -> BudgetStatus:
        remaining = self.remaining_budget(actual_sli)
        if remaining <= 0:
            return BudgetStatus.EXHAUSTED
        if remaining < 0.25:
            return BudgetStatus.CRITICAL
        if remaining < 0.75:
            return BudgetStatus.WARNING
        return BudgetStatus.HEALTHY
```

## Usage

1. Instantiate `ErrorBudget` with the SLO target and window.
2. Call `remaining_budget` with the current SLI.
3. Use `get_status` to map to healthy/warning/critical actions.
