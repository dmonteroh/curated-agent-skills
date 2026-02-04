# Game Day Observation Template

Provides a data model for capturing game day observations and metrics.

## Usage

1. Record observations during each scenario with timestamps.
2. Populate metrics once the scenario completes.
3. Summarize the metrics in the final report.

## Verification

- Confirm all scenarios include at least one observation.
- Validate calculated MTTR matches the observed timeline.

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class GameDayObservation:
    timestamp: datetime
    observer: str
    scenario: str
    observation: str
    category: str  # technical, process, communication, surprise
    severity: str  # info, concern, critical
    photo_url: str = ""

@dataclass
class GameDayMetrics:
    scenario_name: str
    start_time: datetime
    end_time: datetime

    time_to_detect_seconds: float
    time_to_respond_seconds: float
    time_to_recover_seconds: float
    error_rate_peak: float
    alerts_fired: List[str] = field(default_factory=list)
    alerts_missed: List[str] = field(default_factory=list)

    responders_involved: int
    escalations_needed: int
    communication_gaps: List[str] = field(default_factory=list)

    met_rto: bool = False
    met_rpo: bool = False
    zero_customer_impact: bool = False

    def calculate_mttr(self) -> float:
        return (self.end_time - self.start_time).total_seconds()

    def success_rate(self) -> float:
        criteria = [
            self.met_rto,
            self.met_rpo,
            self.zero_customer_impact,
            len(self.alerts_missed) == 0
        ]
        return sum(criteria) / len(criteria) * 100

metrics = GameDayMetrics(
    scenario_name="Database Failover",
    start_time=datetime.fromisoformat("YYYY-MM-DDTHH:MM:SS"),
    end_time=datetime.fromisoformat("YYYY-MM-DDTHH:MM:SS"),
    time_to_detect_seconds=15.0,
    time_to_respond_seconds=45.0,
    time_to_recover_seconds=150.0,
    error_rate_peak=0.05,
    alerts_fired=["DatabaseConnectionError", "HighLatency"],
    alerts_missed=["FailoverInitiated"],
    responders_involved=3,
    escalations_needed=0,
    met_rto=True,
    met_rpo=True,
    zero_customer_impact=True
)

print(f"MTTR: {metrics.calculate_mttr()}s")
print(f"Success Rate: {metrics.success_rate()}%")
```
