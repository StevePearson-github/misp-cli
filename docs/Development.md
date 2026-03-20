# Development

## Project Structure

```
misp-cli/
├── pyproject.toml          # Project configuration
├── README.md              # This file
├── src/
│   └── misp_cli/
│       ├── __init__.py    # Package initialization
│       ├── __main__.py     # Entry point
│       ├── cli/
│       │   ├── app.py      # Main CLI application
│       │   └── commands/   # Command modules
│       └── core/
│           ├── client.py   # MISP API client
│           ├── config.py  # Configuration management
│           └── exceptions.py
├── tests/                  # Test suite
└── docs/                   # Documentation
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=misp_cli

# Run specific test file
uv run pytest tests/test_events.py
```

## Code Quality

```bash
# Run linting
uv run ruff check src/misp_cli/

# Format code
uv run black src/misp_cli/

# Type checking
uv run mypy src/misp_cli/
```

## Adding New Commands

To add a new command module:

1. Create a new file in `src/misp_cli/cli/commands/`
2. Define a Typer app for your commands
3. Import and register the app in `src/misp_cli/cli/app.py`

Example command structure:

```python
import typer
from misp_cli.core.client import MISPCLient
from misp_cli.core.config import MISPConfig

myapp = typer.Typer(help="Manage my resource")

@myapp.command("list")
def list_resources():
    """List resources."""
    config = MISPConfig.from_file()
    client = MISPCLient(
        base_url=config.url,
        api_key=config.api_key,
        verify_ssl=config.verify_ssl,
    )
    # Your implementation here
```
