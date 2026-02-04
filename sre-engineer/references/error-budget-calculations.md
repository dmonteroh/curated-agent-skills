# Error Budget Calculations

```python
class ErrorBudgetCalculator:
    """Calculate and track error budget consumption."""

    def __init__(self, slo_target: float, window_days: int = 30):
        self.slo_target = slo_target
        self.window_days = window_days
        self.total_budget = 1 - slo_target

    def calculate_budget_status(self, good_events: int, total_events: int) -> dict:
        if total_events == 0:
            sli = 1.0
        else:
            sli = good_events / total_events

        budget_used = 1 - sli
        budget_remaining = self.total_budget - budget_used
        budget_remaining_pct = (
            (budget_remaining / self.total_budget * 100)
            if self.total_budget > 0 else 0
        )

        burn_rate = budget_used / self.total_budget if self.total_budget > 0 else 0
        if burn_rate > 0:
            days_to_exhaustion = budget_remaining / budget_used * self.window_days
        else:
            days_to_exhaustion = float('inf')

        return {
            'sli': sli,
            'slo_target': self.slo_target,
            'compliant': sli >= self.slo_target,
            'budget_total': self.total_budget,
            'budget_used': budget_used,
            'budget_remaining': budget_remaining,
            'budget_remaining_pct': budget_remaining_pct,
            'burn_rate': burn_rate,
            'days_to_exhaustion': days_to_exhaustion,
            'good_events': good_events,
            'total_events': total_events,
        }
```

## Usage

1. Instantiate `ErrorBudgetCalculator` with the SLO target and window.
2. Pass good/total event counts to `calculate_budget_status`.
3. Use `burn_rate` and `days_to_exhaustion` to drive policy decisions.
