# AGENTS.md

This document provides guidelines for AI agents working on the misp-cli codebase.

## Build, Lint, and Test Commands

### Installation
```bash
pip install -e ".[dev]"  # Install with dev dependencies
pip install -e ".[test]"  # Install with test dependencies
```

### Running Tests
```bash
pytest                          # Run all tests
pytest tests/test_events.py     # Run specific test file
pytest tests/test_events.py::test_list_events  # Run specific test
pytest -v                      # Verbose output
pytest --cov                   # With coverage report
```

### Type Checking
```bash
mypy src/misp_cli/             # Run mypy type checker
```

### Linting and Formatting
```bash
ruff check src/misp_cli/        # Lint with ruff
ruff check --fix src/misp_cli/  # Lint and auto-fix
black src/misp_cli/             # Format with black
```

### All Checks (CI)
```bash
ruff check && black --check && mypy
```

## Code Style Guidelines

### Imports
Order imports in this sequence with blank lines between groups:
1. Standard library (`import os`, `from typing import ...`)
2. Third-party packages (`import httpx`, `import typer`, `from pydantic import ...`)
3. Local application imports (`from misp_cli.core.config import ...`)

Example:
```python
"""Module docstring."""

import asyncio
import json
from datetime import date
from typing import Any, Dict, List, Optional

import typer
from rich.table import Table

from misp_cli.core.config import MISPProfile
from misp_cli.core.exceptions import MISPAPIError
```

### Type Hints
- Use `typing` module for Python 3.11 compatibility: `Optional[X]`, `Dict[K, V]`, `List[X]`, `Any`
- Always specify return types for functions
- Use explicit type annotations for function parameters
- Avoid `Union` when `Optional` suffices

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `MISPCLient`, `MISPAPIError`, `ConfigManager`)
- **Functions/variables**: `snake_case` (e.g., `get_client`, `format_as_csv`, `api_key`)
- **Constants**: `SCREAMING_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT = 30`)
- **Private methods**: Leading underscore (e.g., `_handle_response`, `_parse_config`)
- **Private attributes**: Leading underscore (e.g., `_client`, `_config_path`)

### File Structure
- Main entry point: `src/misp_cli/__main__.py`
- CLI app: `src/misp_cli/cli/app.py`
- Commands: `src/misp_cli/cli/commands/*.py`
- Core functionality: `src/misp_cli/core/*.py`
- Tests: `tests/` (mirrors source structure)

### Exception Handling
Use the custom exception hierarchy from `misp_cli.core.exceptions`:

```python
from misp_cli.core.exceptions import (
    MISPError,
    MISPAPIError,
    MISPConnectionError,
    MISPAuthenticationError,
    MISPNotFoundError,
    MISPRateLimitError,
    MISPValidationError,
)
```

- Catch specific exceptions, not bare `except Exception`
- Use `raise typer.Exit(code)` for CLI exit with status codes
- Add helpful error messages with suggestions when raising exceptions

### Pydantic Models
Use Pydantic `BaseModel` for configuration and data models:

```python
from pydantic import BaseModel, Field, field_validator

class MISPProfile(BaseModel):
    url: str = Field(..., description="Base URL of MISP instance")
    api_key: str = Field(..., description="MISP API authentication key")
    verify_ssl: bool = Field(default=True)
    timeout: int = Field(default=30, ge=1, le=300)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v.rstrip("/")
```

### Typer CLI Commands
Structure CLI commands using Typer sub-apps:

```python
import typer

events_app = typer.Typer(
    name="events",
    help="Manage MISP events",
    add_help_option=True,
    invoke_without_command=True,
)

@events_app.callback()
def events_callback(ctx: typer.Context, help: bool = typer.Option(...)):
    """Manage MISP events."""

@events_app.command("list")
def list_events(
    limit: int = typer.Option(50, "-l", "--limit"),
    json_output: bool = typer.Option(False, "--json"),
):
    """List events with pagination and filtering."""
    # Command implementation
```

### Async/Sync Patterns
The codebase uses async HTTP client with synchronous wrappers for CLI:

```python
class MISPCLient:
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Async GET request."""
        ...

    def get_sync(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Synchronous GET request wrapper."""
        return asyncio.run(self.get(endpoint, params))
```

### Line Length
Maximum line length: **100 characters** (configured in pyproject.toml).

### Output Formatting
Support multiple output formats (json, table, csv):

```python
def _print_json(data: Any) -> None:
    """Print data as formatted JSON."""
    typer.echo(json.dumps(data, indent=2, default=str))

def _print_table(data: List[Dict], columns: Optional[List[str]] = None) -> None:
    """Print data as a table using Rich."""
    ...
```

### Docstrings
- Use triple double quotes for docstrings
- Module docstrings required at top of every file
- Public functions should have docstrings explaining parameters and return values
- Use complete sentences ending with periods

### Error Messages
- Write clear, actionable error messages
- Include relevant IDs or values in error messages
- Suggest solutions when appropriate
- Use `typer.echo(..., err=True)` for error output

### Testing Patterns
- Use `pytest` with `pytest-asyncio` for async tests
- Use `pytest-mock` for mocking
- Use `respx` for HTTP request mocking
- Test file naming: `test_<module>.py`
- Mirror test structure to source structure

Example test:
```python
def test_list_events(mocker):
    mock_get = mocker.patch.object(client, "get_sync", return_value={"events": []})
    result = runner.invoke(app, ["events", "list"])
    assert mock_get.called
    assert result.exit_code == 0
```
