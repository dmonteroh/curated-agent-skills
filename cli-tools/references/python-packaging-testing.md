# Python Packaging & Testing

## pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "mycli"
version = "1.0.0"
description = "My awesome CLI tool"
requires-python = ">=3.10"
dependencies = [
    "typer[all]>=0.9.0",
    "rich>=13.0.0",
    "questionary>=2.0.0",
]

[project.scripts]
mycli = "mycli.cli:main"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]
```

## Testing CLIs

```python
from typer.testing import CliRunner
from mycli.cli import app

runner = CliRunner()

def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "1.0.0" in result.stdout

def test_init():
    result = runner.invoke(app, ["init", "my-project"])
    assert result.exit_code == 0
    assert "Creating my-project" in result.stdout

def test_init_with_template():
    result = runner.invoke(app, ["init", "my-project", "--template", "react"])
    assert result.exit_code == 0
    assert "react" in result.stdout

def test_invalid_command():
    result = runner.invoke(app, ["invalid"])
    assert result.exit_code != 0
```
