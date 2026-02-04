# Blast Radius Control

Provides a configuration model for progressive blast radius expansion.

## Prerequisites

- Python 3.10+ for `Enum` and type annotations.

## Usage

1. Define blast radius levels and constraints.
2. Validate configurations before execution.
3. Use the progressive rollout list to stage experimentation.

## Verification

- Confirm production configurations enforce feature flags and auto-rollback.

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
