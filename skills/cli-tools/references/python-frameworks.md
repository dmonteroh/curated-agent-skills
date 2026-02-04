# Python CLI Frameworks

## Typer (Recommended)

```python
#!/usr/bin/env python3
import typer
from typing import Optional
from enum import Enum

app = typer.Typer()

class Environment(str, Enum):
    dev = "development"
    staging = "staging"
    prod = "production"

@app.command()
def init(
    name: str = typer.Argument(..., help="Project name"),
    template: str = typer.Option("default", help="Project template"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing"),
):
    """Initialize a new project"""
    typer.echo(f"Creating {name} from {template}")
    if force:
        typer.echo("Force mode enabled")

@app.command()
def deploy(
    environment: Environment = typer.Argument(..., help="Target environment"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview only"),
    config: Optional[typer.FileText] = typer.Option(None, help="Config file"),
):
    """Deploy to environment"""
    if dry_run:
        typer.echo(f"Would deploy to: {environment.value}")
    else:
        typer.echo(f"Deploying to {environment.value}...")

config_app = typer.Typer()
app.add_typer(config_app, name="config", help="Manage configuration")

@config_app.command("get")
def config_get(key: str):
    """Get config value"""
    typer.echo(f"Value: {get_config(key)}")

@config_app.command("set")
def config_set(key: str, value: str):
    """Set config value"""
    set_config(key, value)
    typer.echo(f"Set {key} = {value}")

if __name__ == "__main__":
    app()
```

## Click

```python
import click

@click.group()
@click.version_option()
def cli():
    """My awesome CLI tool"""
    pass

@cli.command()
@click.argument('name')
@click.option('--template', default='default', help='Project template')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing')
def init(name, template, force):
    """Initialize a new project"""
    click.echo(f"Creating {name} from {template}")

@cli.command()
@click.argument('environment', type=click.Choice(['dev', 'staging', 'prod']))
@click.option('--dry-run', is_flag=True, help='Preview only')
@click.option('--config', type=click.File('r'), help='Config file')
def deploy(environment, dry_run, config):
    """Deploy to environment"""
    if dry_run:
        click.secho(f"Would deploy to: {environment}", fg='yellow')
    else:
        click.secho(f"Deploying to {environment}...", fg='green')

@cli.group()
def config():
    """Manage configuration"""
    pass

@config.command('get')
@click.argument('key')
def config_get(key):
    """Get config value"""
    click.echo(get_config(key))

@config.command('set')
@click.argument('key')
@click.argument('value')
def config_set(key, value):
    """Set config value"""
    set_config(key, value)

if __name__ == '__main__':
    cli()
```

## Argparse (Standard Library)

```python
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        prog='mycli',
        description='My awesome CLI tool',
    )
    parser.add_argument('--version', action='version', version='1.0.0')

    subparsers = parser.add_subparsers(dest='command', required=True)

    init_parser = subparsers.add_parser('init', help='Initialize project')
    init_parser.add_argument('name', help='Project name')
    init_parser.add_argument('--template', default='default', help='Template')
    init_parser.add_argument('-f', '--force', action='store_true')

    deploy_parser = subparsers.add_parser('deploy', help='Deploy')
    deploy_parser.add_argument(
        'environment',
        choices=['dev', 'staging', 'prod'],
        help='Target environment'
    )
    deploy_parser.add_argument('--dry-run', action='store_true')
    deploy_parser.add_argument('--config', type=argparse.FileType('r'))

    args = parser.parse_args()

    if args.command == 'init':
        init(args.name, args.template, args.force)
    elif args.command == 'deploy':
        deploy(args.environment, args.dry_run, args.config)

if __name__ == '__main__':
    main()
```
