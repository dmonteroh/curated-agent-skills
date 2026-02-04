# Hypothesis & Blast Radius Patterns

Provides helper patterns for hypothesis writing and blast radius controls.

## Usage

1. Generate a hypothesis statement with clear “given/when/then.”
2. Choose a blast radius level and validate guardrails.
3. Expand progressively only after prior phases succeed.

## Verification

- Confirm the hypothesis maps to measurable metrics.
- Validate blast radius limits align with ownership and rollback.

## Hypothesis Helper

```python
def create_hypothesis(component: str, failure: str, expected_behavior: str) -> dict:
    """
    Create well-formed chaos hypothesis.

    Format: "Given [normal state], when [failure occurs],
             then [expected behavior], measured by [metrics]"
    """
    return {
        "given": f"System is in steady state with {component} functioning normally",
        "when": f"{failure} occurs",
        "then": expected_behavior,
        "measured_by": [
            "Error rate remains below threshold",
            "Latency stays within SLO",
            "No data loss or corruption",
            "Recovery time within RTO"
        ]
    }

hypothesis = create_hypothesis(
    component="payment service",
    failure="50% packet loss to payment gateway",
    expected_behavior="Requests timeout gracefully, retry queue activates, "
                     "users see clear error messages"
)
```

## Blast Radius Control

```python
from dataclasses import dataclass
from enum import Enum

class BlastRadiusLevel(Enum):
    MINIMAL = "single_instance_dev"
    LOW = "single_instance_staging"
    MEDIUM = "percentage_staging"
    HIGH = "percentage_production"
    CRITICAL = "full_production"

@dataclass
class BlastRadiusConfig:
    level: BlastRadiusLevel
    environment: str
    target_percentage: float
    canary_users: list[str]
    feature_flag: str
    auto_rollback: bool
    max_duration_seconds: int

    def validate(self):
        if self.level == BlastRadiusLevel.CRITICAL:
            raise ValueError("CRITICAL blast radius requires explicit approval")

        if self.environment == "production" and self.target_percentage > 10:
            if not self.feature_flag or not self.auto_rollback:
                raise ValueError("Production >10% requires feature flag AND auto-rollback")

        if self.max_duration_seconds > 600:
            raise ValueError("Max duration cannot exceed 10 minutes without approval")

def progressive_rollout() -> list[BlastRadiusConfig]:
    return [
        BlastRadiusConfig(
            level=BlastRadiusLevel.MINIMAL,
            environment="dev",
            target_percentage=100,
            canary_users=[],
            feature_flag="chaos_dev",
            auto_rollback=True,
            max_duration_seconds=300
        ),
        BlastRadiusConfig(
            level=BlastRadiusLevel.LOW,
            environment="staging",
            target_percentage=100,
            canary_users=[],
            feature_flag="chaos_staging",
            auto_rollback=True,
            max_duration_seconds=600
        ),
        BlastRadiusConfig(
            level=BlastRadiusLevel.MEDIUM,
            environment="production",
            target_percentage=1,
            canary_users=["internal_team"],
            feature_flag="chaos_prod_canary",
            auto_rollback=True,
            max_duration_seconds=300
        )
    ]
```
