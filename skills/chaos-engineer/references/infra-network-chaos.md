# Network Latency Injection

Provides a Toxiproxy client for network latency and bandwidth chaos.

## Prerequisites

- Toxiproxy server reachable from the client.
- Python package: `requests`.

## Usage

1. Start Toxiproxy and create a proxy for the target upstream.
2. Apply latency or bandwidth toxics for the experiment duration.
3. Remove toxics after rollback.

## Verification

- Validate latency impact with synthetic requests.
- Confirm removal restores baseline performance.

```python
import requests

class ToxiproxyClient:
    def __init__(self, host: str = "localhost:8474"):
        self.base_url = f"http://{host}"

    def create_proxy(self, name: str, listen: str, upstream: str):
        response = requests.post(f"{self.base_url}/proxies", json={
            "name": name,
            "listen": listen,
            "upstream": upstream,
            "enabled": True
        })
        return response.json()

    def add_latency(self, proxy: str, latency_ms: int, jitter_ms: int = 0):
        return requests.post(
            f"{self.base_url}/proxies/{proxy}/toxics",
            json={
                "name": "latency",
                "type": "latency",
                "attributes": {
                    "latency": latency_ms,
                    "jitter": jitter_ms
                }
            }
        )

    def add_bandwidth_limit(self, proxy: str, rate_kb: int):
        return requests.post(
            f"{self.base_url}/proxies/{proxy}/toxics",
            json={
                "name": "bandwidth",
                "type": "bandwidth",
                "attributes": {"rate": rate_kb}
            }
        )

    def add_timeout(self, proxy: str, timeout_ms: int):
        return requests.post(
            f"{self.base_url}/proxies/{proxy}/toxics",
            json={
                "name": "timeout",
                "type": "timeout",
                "attributes": {"timeout": timeout_ms}
            }
        )

toxiproxy = ToxiproxyClient()

toxiproxy.create_proxy(
    name="postgres",
    listen="0.0.0.0:5433",
    upstream="postgres:5432"
)

toxiproxy.add_latency("postgres", latency_ms=200, jitter_ms=50)
```
