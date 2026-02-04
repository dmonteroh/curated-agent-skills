# Python Terminal Output

## Rich

```python
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

# Styled output
console.print("[bold blue]Info:[/] Starting deployment...")
console.print("[bold green]Success:[/] Deployment complete!")
console.print("[bold yellow]Warning:[/] Deprecated flag used")
console.print("[bold red]Error:[/] Deployment failed")

# Tables
table = Table(title="Deployments")
table.add_column("Environment", style="cyan")
table.add_column("Status", style="magenta")
table.add_column("Time", style="green")

table.add_row("Production", "✓ Success", "2m 34s")
table.add_row("Staging", "✗ Failed", "1m 12s")
console.print(table)

# Panels
console.print(Panel.fit(
    "Deploy to production?",
    title="Confirmation",
    border_style="red"
))

# Syntax highlighting
code = '''
def deploy(env: str):
    print(f"Deploying to {env}")
'''
console.print(Syntax(code, "python", theme="monokai"))

# Progress bars
with Progress() as progress:
    task = progress.add_task("[cyan]Deploying...", total=100)
    for i in range(100):
        do_work()
        progress.update(task, advance=1)

# Spinners
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
) as progress:
    task = progress.add_task("Installing dependencies...")
    install_dependencies()
```
