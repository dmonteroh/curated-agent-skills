# Alert Fatigue Metrics

```python
from dataclasses import dataclass

@dataclass
class AlertQualityMetrics:
    """Track alert quality to prevent fatigue."""
    total_alerts: int
    actionable_alerts: int
    false_positives: int
    auto_resolved: int

    @property
    def precision(self) -> float:
        if self.total_alerts == 0:
            return 0.0
        return (self.actionable_alerts / self.total_alerts) * 100

    @property
    def toil_ratio(self) -> float:
        if self.total_alerts == 0:
            return 0.0
        return ((self.actionable_alerts + self.false_positives) / self.total_alerts) * 100
```

Target alert quality: >90% precision, <30% toil ratio.
