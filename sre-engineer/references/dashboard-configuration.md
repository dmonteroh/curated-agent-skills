# Dashboard Configuration

```python
from grafana_dashboard import Dashboard, Panel, Target

def create_slo_dashboard(service: str) -> dict:
    """Create SLO monitoring dashboard for a service."""

    dashboard = Dashboard(
        title=f"{service} - SLO Dashboard",
        tags=["slo", "sre", service],
        refresh="1m",
    )

    dashboard.add_panel(
        Panel(
            title="Availability SLI (30d)",
            targets=[
                Target(
                    expr=f"""
                    sum(rate(http_requests_total{{
                        status=~"2..",
                        service="{service}"
                    }}[30d]))
                    /
                    sum(rate(http_requests_total{{service="{service}"}}[30d]))
                    """,
                    legendFormat="Current SLI",
                ),
            ],
            thresholds=[
                {"value": 0.999, "color": "red"},
                {"value": 0.9995, "color": "yellow"},
                {"value": 1.0, "color": "green"},
            ],
        )
    )

    dashboard.add_panel(
        Panel(
            title="Error Budget Remaining",
            targets=[
                Target(
                    expr=f"""
                    (0.001 - (1 - (
                      sum(rate(http_requests_total{{
                          status=~"2..",
                          service="{service}"
                      }}[30d]))
                      /
                      sum(rate(http_requests_total{{service="{service}"}}[30d]))
                    ))) / 0.001 * 100
                    """,
                    legendFormat="Budget Remaining %",
                ),
            ],
            unit="percent",
        )
    )

    dashboard.add_panel(
        Panel(
            title="Error Budget Burn Rate",
            targets=[
                Target(
                    expr=f"""
                    (1 - (
                      sum(rate(http_requests_total{{
                          status=~"2..",
                          service="{service}"
                      }}[1h]))
                      /
                      sum(rate(http_requests_total{{service="{service}"}}[1h]))
                    )) / 0.001
                    """,
                    legendFormat="1h burn rate",
                ),
            ],
            thresholds=[
                {"value": 1.0, "color": "green"},
                {"value": 6.0, "color": "yellow"},
                {"value": 14.4, "color": "red"},
            ],
        )
    )

    dashboard.add_row("Golden Signals")

    dashboard.add_panel(
        Panel(
            title="Latency (P50, P95, P99)",
            targets=[
                Target(
                    expr=f'service:http_request_duration_seconds:p50{{service="{service}"}}',
                    legendFormat="p50",
                ),
                Target(
                    expr=f'service:http_request_duration_seconds:p95{{service="{service}"}}',
                    legendFormat="p95",
                ),
                Target(
                    expr=f'service:http_request_duration_seconds:p99{{service="{service}"}}',
                    legendFormat="p99",
                ),
            ],
            unit="s",
        )
    )

    return dashboard.to_json()
```

## Requirements

- Python environment with a `grafana_dashboard` SDK module.

## Usage

1. Call `create_slo_dashboard("service-name")` and apply the JSON output.
2. Review the panel thresholds against SLO targets.

## Verification

- Confirm dashboards render and queries return data.
