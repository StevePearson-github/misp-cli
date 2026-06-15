"""Shared output utilities for MISP CLI commands."""

import json
from typing import Any

import typer
from rich.table import Table

from misp_cli.core.config import MISPProfile

_TABLE_PRIORITY_COLUMNS = [
    "id",
    "name",
    "info",
    "title",
    "value",
    "type",
    "category",
    "date",
    "timestamp",
    "published",
    "status",
    "distribution",
    "org",
    "email",
]
_TABLE_MAX_COLUMNS = 8


def get_output_format(
    config: MISPProfile,
    json_output: bool,
    table_output: bool,
    csv_output: bool = False,
) -> str:
    """Determine output format based on options and config."""
    if csv_output:
        return "csv"
    if table_output:
        return "table"
    if json_output:
        return "json"
    return config.output_format


def print_csv(data: list[dict], columns: list[str] | None = None) -> None:
    """Print data as CSV."""
    from misp_cli.core.client import MISPCLient

    csv_output = MISPCLient.format_as_csv(data, columns)
    if csv_output:
        typer.echo(csv_output)


def print_json(data: Any) -> None:
    """Print data as formatted JSON."""
    typer.echo(json.dumps(data, indent=2, default=str))


def print_table(data: list[dict], columns: list[str] | None = None) -> None:
    """Print data as a table."""
    if not data:
        typer.echo("No data available")
        return

    from misp_cli.cli.app import get_app
    from misp_cli.core.client import MISPCLient

    console = get_app().console

    # Flatten nested dictionaries
    flattened_data = [MISPCLient.flatten_dict(row) for row in data]

    if columns:
        display_columns = list(columns)
    else:
        available = list(flattened_data[0].keys())
        if len(available) > _TABLE_MAX_COLUMNS:
            chosen = [c for c in _TABLE_PRIORITY_COLUMNS if c in available][:_TABLE_MAX_COLUMNS]
            remaining_slots = _TABLE_MAX_COLUMNS - len(chosen)
            if remaining_slots > 0:
                chosen += [c for c in available if c not in chosen][:remaining_slots]
            display_columns = chosen
        else:
            display_columns = available

    table = Table(show_header=True, header_style="bold magenta")
    for col in display_columns:
        table.add_column(col.replace("_", " ").title())

    for item in flattened_data:
        row = [
            str(item.get(col, "")) if item.get(col) is not None else "" for col in display_columns
        ]
        table.add_row(*row)

    console.print(table)


COUNT_OPTION = typer.Option(False, "--count", help="Return count instead of listing results")


def print_count(items: list[Any], json_output: bool) -> None:
    """Print count of items and exit. Caller must ensure items is the full (unlimited) list."""
    if json_output:
        print_json({"count": len(items)})
    else:
        typer.echo(str(len(items)))
    raise typer.Exit()


def unwrap_nested_data(
    response: list[dict] | dict,
    key: str,
) -> list[dict]:
    """
    Unwrap nested MISP API response data.

    Args:
        response: API response (list or dict)
        key: The key to unwrap from nested items (e.g., "Tag", "Event", "User")

    Returns:
        Flattened list of dictionaries
    """
    if isinstance(response, list):
        return [item.get(key, item) for item in response]
    elif isinstance(response, dict):
        raw = response.get(key, response.get("data", []))
        if isinstance(raw, list):
            return [item.get(key, item) for item in raw]
        return [raw] if raw else []
    return []
