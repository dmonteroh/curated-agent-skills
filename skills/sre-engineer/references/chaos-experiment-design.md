# Chaos Experiment Design

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ExperimentStatus(Enum):
    PLANNED = "planned"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ABORTED = "aborted"

@dataclass
class ChaosExperiment:
    name: str
    hypothesis: str
    blast_radius: str
    rollback_plan: str
    success_criteria: str
    status: ExperimentStatus = ExperimentStatus.PLANNED
    started_at: datetime | None = None
    completed_at: datetime | None = None
    observations: list[str] | None = None

    def should_abort(self, metrics: dict) -> bool:
        if metrics.get('error_rate', 0) > 0.10:
            return True
        if metrics.get('latency_p99', 0) > 2.0:
            return True
        return False
```
