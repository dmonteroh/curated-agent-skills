# SLI Definition Patterns

Service Level Indicators are quantitative measurements of service behavior.

## Request-Based SLIs

```python
def calculate_availability_sli(metrics):
    """Calculate availability SLI from request metrics."""
    successful_requests = metrics['http_2xx'] + metrics['http_4xx']
    total_requests = metrics['total_requests']

    if total_requests == 0:
        return 1.0

    return successful_requests / total_requests
```

## Latency-Based SLIs

```python
def calculate_latency_sli(latency_histogram, threshold_ms=500):
    """Calculate latency SLI from histogram."""
    fast_requests = sum(
        count for bucket, count in latency_histogram.items()
        if bucket <= threshold_ms
    )
    total_requests = sum(latency_histogram.values())

    return fast_requests / total_requests if total_requests > 0 else 1.0
```
