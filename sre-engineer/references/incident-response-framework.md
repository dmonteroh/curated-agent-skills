# Incident Response Framework

Structured approach to incident management.

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class Severity(Enum):
    SEV1 = "critical"
    SEV2 = "high"
    SEV3 = "medium"
    SEV4 = "low"

@dataclass
class Incident:
    id: str
    title: str
    severity: Severity
    started_at: datetime
    detected_at: datetime
    resolved_at: datetime | None = None
    root_cause: str | None = None
    impact: str | None = None

    @property
    def detection_time(self) -> float:
        delta = self.detected_at - self.started_at
        return delta.total_seconds() / 60

    @property
    def mttr(self) -> float | None:
        if not self.resolved_at:
            return None
        delta = self.resolved_at - self.detected_at
        return delta.total_seconds() / 60

    @property
    def total_duration(self) -> float | None:
        if not self.resolved_at:
            return None
        delta = self.resolved_at - self.started_at
        return delta.total_seconds() / 60

incident = Incident(
    id="INC-EXAMPLE-001",
    title="Database connection pool exhaustion",
    severity=Severity.SEV2,
    started_at=datetime(2023, 1, 15, 14, 30),
    detected_at=datetime(2023, 1, 15, 14, 35),
    resolved_at=datetime(2023, 1, 15, 15, 10),
    root_cause="Connection leak in payment service",
    impact="Payment processing delayed for 15% of users",
)
```
