# Gremlin Chaos Integration

Provides a Gremlin API client example for launching and halting chaos attacks.

## Prerequisites

- Gremlin API key and team ID with permission to launch attacks.
- Network access to the Gremlin API endpoint (`https://api.gremlin.com`).
- Targets are labeled and reachable by Gremlin agents.

## Usage

1. Configure the client with API key and team ID.
2. Choose the attack type and targets.
3. Record the attack ID in the experiment log.
4. Halt the attack after the duration or on guardrail breach.

## Verification

- Confirm the API response returns a valid attack ID.
- Check the Gremlin UI or API for attack status transitions.
- Validate steady-state metrics recover after halting the attack.

## Example Client

```python
import requests
from typing import Literal

class GremlinClient:
    def __init__(self, api_key: str, team_id: str):
        self.api_key = api_key
        self.team_id = team_id
        self.base_url = "https://api.gremlin.com/v1"
        self.headers = {
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json"
        }

    def create_cpu_attack(
        self,
        targets: list[str],
        length: int = 60,
        cores: int = 1,
        percent: int = 50
    ):
        """Launch CPU resource attack."""
        payload = {
            "command": {
                "type": "cpu",
                "args": [
                    "-l", str(length),
                    "-c", str(cores),
                    "-p", str(percent)
                ]
            },
            "target": {
                "type": "Exact",
                "exact": targets
            }
        }

        response = requests.post(
            f"{self.base_url}/attacks/new",
            headers=self.headers,
            json=payload
        )
        return response.json()

    def create_network_attack(
        self,
        targets: list[str],
        attack_type: Literal["latency", "packet_loss", "blackhole"],
        length: int = 60,
        **kwargs
    ):
        """Launch network attack."""
        args = ["-l", str(length)]

        if attack_type == "latency":
            args.extend(["-m", str(kwargs.get('delay_ms', 100))])
            if 'jitter_ms' in kwargs:
                args.extend(["-j", str(kwargs['jitter_ms'])])

        elif attack_type == "packet_loss":
            args.extend(["-p", str(kwargs.get('percent', 10))])

        elif attack_type == "blackhole":
            if 'port' in kwargs:
                args.extend(["--port", str(kwargs['port'])])
            if 'protocol' in kwargs:
                args.extend(["--protocol", kwargs['protocol']])

        payload = {
            "command": {
                "type": attack_type,
                "args": args
            },
            "target": {
                "type": "Exact",
                "exact": targets
            }
        }

        response = requests.post(
            f"{self.base_url}/attacks/new",
            headers=self.headers,
            json=payload
        )
        return response.json()

    def halt_attack(self, attack_id: str):
        """Stop running attack."""
        response = requests.delete(
            f"{self.base_url}/attacks/{attack_id}",
            headers=self.headers
        )
        return response.status_code == 200

    def create_scenario(self, name: str, attacks: list[dict]):
        """Create reusable attack scenario."""
        payload = {
            "name": name,
            "description": f"Chaos scenario: {name}",
            "graph": {
                "nodes": attacks
            }
        }

        response = requests.post(
            f"{self.base_url}/scenarios",
            headers=self.headers,
            json=payload
        )
        return response.json()

gremlin = GremlinClient(api_key="...", team_id="...")

gremlin.create_cpu_attack(
    targets=["container-id-123", "container-id-456"],
    length=300,
    cores=2,
    percent=80
)

gremlin.create_network_attack(
    targets=["host-abc"],
    attack_type="latency",
    length=180,
    delay_ms=500,
    jitter_ms=100
)
```
