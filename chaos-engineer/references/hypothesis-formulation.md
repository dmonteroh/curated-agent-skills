# Hypothesis Formulation

Provides a template function for consistent hypotheses.

## Prerequisites

- Python 3.10+ for type annotations.

## Usage

1. Replace `component`, `failure`, and `expected_behavior` with the experiment scope.
2. Store the output in the experiment spec.

## Verification

- Confirm hypothesis includes steady state, failure, and expected behavior.

```python
def create_hypothesis(component: str, failure: str, expected_behavior: str) -> dict:
    """
    Format: "Given [normal state], when [failure occurs], then [expected behavior]"
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
    expected_behavior="Requests timeout gracefully, retry queue activates, users see clear error messages"
)
```
