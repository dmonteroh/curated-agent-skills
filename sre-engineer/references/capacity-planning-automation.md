# Capacity Planning Automation

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np

@dataclass
class CapacityMetrics:
    timestamp: datetime
    requests_per_second: float
    cpu_utilization: float
    memory_utilization: float

class CapacityPlanner:
    """Automated capacity planning and forecasting."""

    def __init__(self, metrics: list[CapacityMetrics]):
        self.metrics = metrics

    def forecast_growth(self, days_ahead: int = 90) -> dict:
        timestamps = [(m.timestamp - self.metrics[0].timestamp).days
                      for m in self.metrics]
        cpu_values = [m.cpu_utilization for m in self.metrics]
        mem_values = [m.memory_utilization for m in self.metrics]

        cpu_trend = np.polyfit(timestamps, cpu_values, deg=1)
        mem_trend = np.polyfit(timestamps, mem_values, deg=1)

        future_day = timestamps[-1] + days_ahead
        cpu_forecast = np.polyval(cpu_trend, future_day)
        mem_forecast = np.polyval(mem_trend, future_day)

        return {
            'days_ahead': days_ahead,
            'cpu_forecast': min(cpu_forecast, 1.0),
            'memory_forecast': min(mem_forecast, 1.0),
            'cpu_threshold_breach': cpu_forecast > 0.8,
            'memory_threshold_breach': mem_forecast > 0.8,
        }

    def recommend_scaling(self, forecast: dict) -> str:
        if forecast['cpu_threshold_breach'] or forecast['memory_threshold_breach']:
            return f"SCALE UP: Forecast shows >80% utilization in {forecast['days_ahead']} days"
        return "OK: No scaling needed"
```

## Requirements

- Python environment with `numpy` installed.

## Usage

1. Build a `CapacityMetrics` list from historical telemetry.
2. Call `forecast_growth` and `recommend_scaling`.
3. Share the forecast as part of quarterly capacity reviews.

## Verification

- Compare the forecast to a held-out time window.
- Ensure alerts trigger when utilization exceeds the threshold.
