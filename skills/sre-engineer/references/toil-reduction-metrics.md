# Toil Reduction Metrics

```python
class ToilTracker:
    """Track toil reduction over time."""

    def __init__(self):
        self.snapshots = []

    def record_snapshot(self, week: int, toil_hours: float, team_hours: float):
        self.snapshots.append({
            'week': week,
            'toil_hours': toil_hours,
            'team_hours': team_hours,
            'toil_percentage': (toil_hours / team_hours * 100) if team_hours > 0 else 0,
        })

    def toil_trend(self) -> str:
        if len(self.snapshots) < 2:
            return "insufficient data"

        first_pct = self.snapshots[0]['toil_percentage']
        last_pct = self.snapshots[-1]['toil_percentage']

        if last_pct < first_pct:
            return f"improving ({first_pct:.1f}% → {last_pct:.1f}%)"
        return f"worsening ({first_pct:.1f}% → {last_pct:.1f}%)"
```

Target toil: <50% of team time, with a long-term goal of <30%.
