# Contributing to MISP CLI

Thank you for your interest in contributing to MISP CLI! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Project Structure](#project-structure)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended) or pip
- Git
- A MISP instance for testing (optional but recommended)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/misp-cli.git
   cd misp-cli
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/StevePearson-github/misp-cli.git
   ```

## Development Setup

### Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Using pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Verify Installation

```bash
# Run tests
pytest

# Run linting
ruff check src/misp_cli/

# Run type checking
mypy src/misp_cli/

# Format code
black src/misp_cli/
```

## Making Changes

### Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Make Your Changes

1. Write clean, well-documented code
2. Add tests for new functionality
3. Update documentation as needed
4. Follow the coding standards below

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=misp_cli

# Run specific test file
pytest tests/test_events.py

# Run specific test
pytest tests/test_events.py::TestEventsCommands::test_events_list_json_output
```

### Code Quality Checks

```bash
# Lint with ruff
ruff check src/misp_cli/

# Auto-fix linting issues
ruff check --fix src/misp_cli/

# Format with black
black src/misp_cli/

# Type check with mypy
mypy src/misp_cli/
```

## Submitting Changes

### Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add support for event proposals (shadow attributes)

- Add proposals list command
- Add proposals accept/discard commands
- Include tests for new commands
- Update documentation"
```

### Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### Open a Pull Request

1. Go to your fork on GitHub
2. Click "Compare & pull request"
3. Fill in the PR template
4. Ensure all CI checks pass
5. Request review from maintainers

### Pull Request Guidelines

- Link any related issues
- Describe the changes and why they're needed
- Include tests for new functionality
- Update documentation as needed
- Keep PRs focused and reasonably sized
- Be responsive to code review feedback

## Coding Standards

### Code Style

- **Line length**: Maximum 100 characters
- **Formatting**: Use Black with default settings
- **Linting**: Follow Ruff rules (configured in `pyproject.toml`)
- **Type hints**: Required for all function parameters and return types

### Import Order

Imports should be grouped in the following order with blank lines between:

1. Standard library imports
2. Third-party imports
3. Local application imports

Example:
```python
"""Module docstring."""

import asyncio
from typing import Any, Dict, Optional

import typer
from rich.table import Table

from misp_cli.core.config import MISPProfile
from misp_cli.core.exceptions import MISPAPIError
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `MISPCLient`, `MISPAPIError`)
- **Functions/variables**: `snake_case` (e.g., `get_client`, `api_key`)
- **Constants**: `SCREAMING_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT`)
- **Private methods**: Leading underscore (e.g., `_handle_response`)

### Documentation

- Add docstrings to all public modules, classes, and functions
- Use triple double quotes for docstrings
- Include parameter descriptions and return types

Example:
```python
def get_event(event_id: int, include_context: bool = False) -> Dict[str, Any]:
    """
    Retrieve a specific MISP event by ID.
    
    Args:
        event_id: The unique identifier of the event
        include_context: Whether to include related context data
    
    Returns:
        Dictionary containing the event data
    
    Raises:
        MISPNotFoundError: If the event doesn't exist
        MISPAPIError: On API errors
    """
```

### Error Handling

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

## Project Structure

```
misp-cli/
├── src/misp_cli/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Entry point
│   ├── cli/
│   │   ├── app.py           # Main CLI application
│   │   └── commands/        # Command modules
│   │       ├── events.py
│   │       ├── attributes.py
│   │       └── ...
│   └── core/
│       ├── client.py        # MISP API client
│       ├── config.py        # Configuration management
│       └── exceptions.py    # Custom exceptions
├── tests/                   # Test suite
├── docs/                    # Documentation
└── pyproject.toml          # Project configuration
```

### Adding New Commands

1. Create a new file in `src/misp_cli/cli/commands/`
2. Define a Typer app for your commands
3. Import and register the app in `src/misp_cli/cli/app.py`
4. Add tests in `tests/`
5. Update documentation

## Getting Help

- Open a [GitHub Issue](https://github.com/StevePearson-github/misp-cli/issues) for bugs or feature requests
- Check existing issues before creating new ones
- Provide as much context as possible

## License

By contributing to MISP CLI, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to MISP CLI! 🎉
