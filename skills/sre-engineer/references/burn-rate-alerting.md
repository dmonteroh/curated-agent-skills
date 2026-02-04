# Burn Rate Alerting

Burn rate measures how fast you're consuming the error budget.

```python
from datetime import timedelta
from typing import NamedTuple

class BurnRateAlert(NamedTuple):
    window: timedelta
    burn_rate_threshold: float
    budget_consumed_threshold: float

    def should_alert(self, current_error_rate: float, total_budget: float) -> bool:
        if total_budget == 0:
            return current_error_rate > 0
        burn_rate = current_error_rate / total_budget
        return burn_rate >= self.burn_rate_threshold

BURN_RATE_ALERTS = [
    BurnRateAlert(window=timedelta(hours=1), burn_rate_threshold=14.4, budget_consumed_threshold=0.02),
    BurnRateAlert(window=timedelta(hours=6), burn_rate_threshold=6.0, budget_consumed_threshold=0.05),
    BurnRateAlert(window=timedelta(days=3), burn_rate_threshold=1.0, budget_consumed_threshold=0.10),
]

def check_burn_rate_alerts(slo_target: float, current_sli: float):
    """Check if any burn rate alerts should fire."""
    error_budget = 1 - slo_target
    error_rate = 1 - current_sli
    return [alert for alert in BURN_RATE_ALERTS if alert.should_alert(error_rate, error_budget)]
```

## Usage

1. Compute `current_sli` from monitoring data.
2. Call `check_burn_rate_alerts` to see which alert windows should fire.
3. Map alert windows to paging vs ticketing policy.
