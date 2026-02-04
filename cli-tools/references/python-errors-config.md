# Python Error Handling & Configuration

## Error Handling

```python
import os
import sys
import typer

app = typer.Typer()

@app.command()
def deploy():
    try:
        perform_deploy()
    except PermissionError:
        typer.secho("Permission denied", fg=typer.colors.RED, err=True)
        typer.echo("Try running with sudo or check file permissions")
        raise typer.Exit(code=77)
    except FileNotFoundError as e:
        typer.secho(f"File not found: {e.filename}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=127)
    except Exception as e:
        typer.secho(f"Deployment failed: {e}", fg=typer.colors.RED, err=True)
        if os.getenv('DEBUG'):
            import traceback
            traceback.print_exc()
        raise typer.Exit(code=1)

def main():
    try:
        app()
    except KeyboardInterrupt:
        typer.echo("\nOperation cancelled")
        sys.exit(130)

if __name__ == "__main__":
    main()
```

## Configuration Management

```python
from pathlib import Path
from typing import Any
import json
import os

class Config:
    def __init__(self):
        self.config_paths = [
            Path("/etc/mycli/config.json"),
            Path.home() / ".config" / "mycli" / "config.json",
            Path.cwd() / "mycli.json",
        ]

    def load(self) -> dict[str, Any]:
        config = self._defaults()

        for path in self.config_paths:
            if path.exists():
                with path.open() as f:
                    config.update(json.load(f))

        for key in config.keys():
            env_var = f"MYCLI_{key.upper()}"
            if env_var in os.environ:
                config[key] = os.environ[env_var]

        return config

    def _defaults(self) -> dict[str, Any]:
        return {
            "environment": "development",
            "verbose": False,
            "timeout": 30,
        }
```
