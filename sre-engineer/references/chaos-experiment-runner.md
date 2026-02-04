# Chaos Experiment Runner

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
import time

@dataclass
class SafetyConstraints:
    max_error_rate: float = 0.10
    max_latency_p99: float = 2.0
    max_duration_minutes: int = 15
    business_hours_only: bool = True

class ChaosRunner:
    """Safely execute chaos experiments with monitoring."""

    def __init__(self, safety: SafetyConstraints):
        self.safety = safety

    def run_experiment(self, experiment, injector, get_metrics):
        if self.safety.business_hours_only:
            current_hour = datetime.now().hour
            if 9 <= current_hour <= 17:
                experiment.status = "aborted"
                experiment.observations = ["Aborted: Business hours constraint"]
                return experiment

        baseline_metrics = get_metrics()
        experiment.observations = [f"Baseline metrics: {baseline_metrics}"]

        experiment.status = "running"
        experiment.started_at = datetime.now()

        try:
            injector.inject()

            start_time = datetime.now()
            max_duration = timedelta(minutes=self.safety.max_duration_minutes)

            while datetime.now() - start_time < max_duration:
                time.sleep(10)
                current_metrics = get_metrics()
                experiment.observations.append(
                    f"{datetime.now().isoformat()}: {current_metrics}"
                )
                if experiment.should_abort(current_metrics):
                    experiment.status = "aborted"
                    break
            else:
                experiment.status = "success"

        except Exception as error:
            experiment.status = "failed"
            experiment.observations.append(f"Exception: {error}")

        finally:
            injector.rollback()
            experiment.completed_at = datetime.now()

        return experiment
```

## Usage

1. Supply a `ChaosExperiment`, injector implementation, and metrics callback.
2. Run the experiment in a controlled environment.
3. Review `experiment.observations` for safety checks and outcomes.

## Verification

- Confirm rollback restores normal operation.
- Verify metrics remain within safety constraints.
