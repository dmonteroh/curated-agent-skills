# Toil Definition and Inventory

Toil is manual, repetitive, automatable work that scales linearly with service growth.

```python
from dataclasses import dataclass
from enum import Enum

class ToilCategory(Enum):
    MANUAL_INTERVENTION = "manual"
    REPETITIVE_TASKS = "repetitive"
    NO_ENDURING_VALUE = "no_value"
    SCALES_WITH_SERVICE = "scales"
    INTERRUPT_DRIVEN = "reactive"

@dataclass
class ToilItem:
    name: str
    frequency_per_week: int
    minutes_per_occurrence: int
    category: ToilCategory
    automation_difficulty: str

    @property
    def weekly_hours(self) -> float:
        return (self.frequency_per_week * self.minutes_per_occurrence) / 60

    @property
    def annual_hours(self) -> float:
        return self.weekly_hours * 52

    def roi_score(self) -> float:
        difficulty_multiplier = {
            'easy': 1.0,
            'medium': 0.5,
            'hard': 0.25,
        }
        return self.annual_hours * difficulty_multiplier.get(
            self.automation_difficulty, 0.1
        )
```
