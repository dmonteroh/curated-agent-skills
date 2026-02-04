# Continuous Chaos Dashboard

Provides a lightweight Flask service for summarizing chaos outcomes from Prometheus.

## Prerequisites

- Python environment with `flask` and `requests` installed.
- Prometheus accessible from the service runtime.
- Metrics for chaos experiments available in Prometheus.

## Usage

1. Configure the Prometheus URL in `ChaosDashboard`.
2. Run the Flask app in a non-production environment.
3. Route dashboards or status pages to `/api/chaos-summary`.

## Verification

- Confirm the endpoint returns experiment and MTTR metrics.
- Validate that metrics align with Prometheus queries.
- Check the service logs for query errors.

## Example Service

```python
from flask import Flask, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

class ChaosDashboard:
    def __init__(self, prometheus_url: str):
        self.prometheus = prometheus_url

    def get_experiment_metrics(self, hours: int = 24):
        end = datetime.now()
        start = end - timedelta(hours=hours)

        query = f'''
            sum by (experiment, verdict) (
                increase(litmuschaos_experiment_verdict[{hours}h])
            )
        '''

        response = requests.get(
            f"{self.prometheus}/api/v1/query",
            params={"query": query}
        )

        return response.json()

    def get_mttr_trend(self):
        query = '''
            avg_over_time(
                avg(
                    time() - timestamp(
                        kube_pod_status_phase{phase="Running"} == 1
                    )
                )[7d:]
            )
        '''

        response = requests.get(
            f"{self.prometheus}/api/v1/query",
            params={"query": query}
        )

        return response.json()

@app.route('/api/chaos-summary')
def chaos_summary():
    dashboard = ChaosDashboard(prometheus_url="http://prometheus:9090")

    return jsonify({
        "experiments": dashboard.get_experiment_metrics(hours=24),
        "mttr_trend": dashboard.get_mttr_trend(),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```
