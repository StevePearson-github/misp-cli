# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`misp-cli` is a typed Python CLI tool for interacting with [MISP](https://www.misp-project.org/) (Malware Information Sharing Platform) instances. It uses **Typer** for the CLI framework, **Rich** for terminal output, **httpx** for async HTTP, and **Pydantic** for data validation.

## Commands

### Install

```bash
uv tool install .                  # Preferred
uv tool install --reinstall .      # Reinstall after changes
uv pip install -e ".[dev]"         # Editable with dev dependencies
```

### Test

```bash
uv run pytest                                                   # All tests
uv run pytest tests/test_events.py                              # Single file
uv run pytest tests/test_events.py::test_list_events            # Single test
uv run pytest -v --cov                                          # Verbose with coverage
```

### Lint, Format, Type Check

```bash
uv run ruff check src/misp_cli/         # Lint
uv run ruff check --fix src/misp_cli/   # Lint with auto-fix
uv run black src/misp_cli/              # Format
uv run mypy src/misp_cli/               # Type check
uv run ruff check && uv run black --check && uv run mypy  # Full CI check
```

## Architecture

### Layer Structure

```
src/misp_cli/
├── __main__.py          # Entry point → wraps app() with KeyboardInterrupt/Exception handling
├── cli/
│   ├── app.py           # MISPApp class (CLI state: console, config, client); global Typer app + callback
│   ├── output.py        # print_json(), print_table(), print_csv() formatting utilities
│   └── commands/        # One module per MISP resource (events, attributes, tags, feeds, etc.)
└── core/
    ├── client.py        # MISPClient: async httpx client + get_sync()/post_sync() wrappers
    ├── config.py        # MISPProfile (Pydantic), ConfigManager (INI parsing)
    └── exceptions.py    # Exception hierarchy: MISPError → MISPAPIError, MISPConnectionError, etc.
```

### Key Design Decisions

- **Async client, sync CLI**: `MISPClient` methods are async; CLI commands call `_sync()` wrappers via `asyncio.run()`.
- **State via `MISPApp`**: Commands receive `ctx.obj` (a `MISPApp` instance) for access to the configured client and console.
- **Output formats**: All list/show commands support `--json`, `--csv`, and default table output via `output.py`.
- **Profiles**: Configuration lives in INI files (`~/.misp-cli.conf`). Multiple named profiles supported. Precedence: `--config` flag > `MISP_CLI_CONFIG` env var > `~/.misp-cli.conf` > `./.misp-cli.conf`.

### Adding a New Command Module

1. Create `src/misp_cli/cli/commands/<resource>.py` with a `typer.Typer` sub-app.
2. Register it in `src/misp_cli/cli/app.py` with `app.add_typer(...)`.
3. Add a corresponding `tests/test_<resource>.py`.

### Testing Pattern

Use `pytest-mock` to patch `MISPClient.get_sync` / `post_sync`; use `respx` for HTTP-level mocking. Tests use Typer's `CliRunner`.

```python
def test_list_events(mocker):
    mock_get = mocker.patch.object(client, "get_sync", return_value={"events": []})
    result = runner.invoke(app, ["events", "list"])
    assert mock_get.called
    assert result.exit_code == 0
```

## Code Style

- **Max line length**: 100 characters (ruff + black configured in `pyproject.toml`).
- **Type hints**: Use `typing` module style (`Optional[X]`, `List[X]`, `Dict[K, V]`) for Python 3.11 compatibility. Always annotate function parameters and return types.
- **Imports**: stdlib → third-party → local, blank line between groups.
- **Exceptions**: Catch specific exceptions from `misp_cli.core.exceptions`; use `raise typer.Exit(code)` for CLI exits.
- **Error output**: Use `typer.echo(..., err=True)` for stderr messages.
