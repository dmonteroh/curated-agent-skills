# Error Budget Decision Framework

Use this framework to make reliability vs velocity tradeoffs.

```python
def should_deploy(
    budget_remaining: float,
    change_risk: str,
    business_priority: str,
) -> tuple[bool, str]:
    """Decide if deployment should proceed."""
    if budget_remaining <= 0:
        if business_priority == 'critical':
            return True, "Critical business need, budget exhausted"
        return False, "Error budget exhausted, feature freeze in effect"

    if budget_remaining < 0.25:
        if change_risk == 'high':
            return False, "High risk change with critical budget"
        if business_priority in ['high', 'critical']:
            return True, "High priority with critical budget - proceed carefully"
        return False, "Budget critical, deferring non-essential changes"

    if budget_remaining < 0.75:
        if change_risk == 'high' and business_priority == 'low':
            return False, "High risk, low priority with warning budget"
        return True, "Approved with enhanced review"

    return True, "Normal operations, budget healthy"
```
