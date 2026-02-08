"""Dashboard and statistics commands for MISP CLI."""

import json
from typing import Any, Dict

import typer
from rich.table import Table

from misp_cli.core.config import MISPProfile

stats_app = typer.Typer(
    name="stats",
    help="View MISP dashboard and statistics",
    add_help_option=True,
    invoke_without_command=True,
)


@stats_app.callback()
def stats_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """View MISP dashboard and statistics."""
    if help:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def _get_output_format(config: MISPProfile, json_output: bool, table_output: bool) -> str:
    """Determine output format based on options and config."""
    if table_output:
        return "table"
    if json_output:
        return "json"
    return config.output_format


def _print_json(data: Any) -> None:
    """Print data as formatted JSON."""
    typer.echo(json.dumps(data, indent=2, default=str))


def _print_table(data: Dict[str, Any], title: str = None) -> None:
    """Print data as a table."""
    from misp_cli.cli.app import get_app
    console = get_app().console
    table = Table(title=title, show_header=True, header_style="bold magenta")

    for key, value in data.items():
        table.add_column(key.replace("_", " ").title())

    row = []
    for value in data.values():
        if value is None:
            row.append("N/A")
        elif isinstance(value, (dict, list)):
            row.append(str(len(value)))
        else:
            row.append(str(value))
    table.add_row(*row)

    console.print(table)


@stats_app.command("system")
def system_stats(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Get system statistics."""
    from misp_cli.cli.app import get_app
    from misp_cli.core.exceptions import MISPAPIError, MISPNotFoundError

    app = get_app()
    config = app.profile
    client = app.client

    try:
        response = client.get_sync("/users/statistics/data.json")
    except MISPNotFoundError as e:
        typer.echo(f"Error: System statistics endpoint not found. Check your MISP version.", err=True)
        raise typer.Exit(1)
    except MISPAPIError as e:
        typer.echo(f"Error fetching system statistics: {e.message}", err=True)
        raise typer.Exit(1)

    output_format = _get_output_format(config, json_output, table_output)

    if output_format == "json" or json_output:
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table(response, "System Statistics")
        else:
            _print_json(response)


@stats_app.command("users")
def user_stats(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Get user statistics."""
    from misp_cli.cli.app import get_app
    from misp_cli.core.exceptions import MISPAPIError, MISPNotFoundError

    app = get_app()
    config = app.profile
    client = app.client

    try:
        response = client.get_sync("/users/statistics.json")
    except MISPNotFoundError as e:
        typer.echo(f"Error: User statistics endpoint not found. Check your MISP version.", err=True)
        raise typer.Exit(1)
    except MISPAPIError as e:
        typer.echo(f"Error fetching user statistics: {e.message}", err=True)
        raise typer.Exit(1)

    output_format = _get_output_format(config, json_output, table_output)

    if output_format == "json" or json_output:
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table(response, "User Statistics")
        else:
            _print_json(response)


@stats_app.command("orgs")
def org_stats(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Get organisation statistics."""
    from misp_cli.cli.app import get_app
    from misp_cli.core.exceptions import MISPAPIError, MISPNotFoundError

    app = get_app()
    config = app.profile
    client = app.client

    try:
        response = client.get_sync("/users/statistics/orgs.json")
    except MISPNotFoundError as e:
        typer.echo(f"Error: Organisation statistics endpoint not found. Check your MISP version.", err=True)
        raise typer.Exit(1)
    except MISPAPIError as e:
        typer.echo(f"Error fetching organisation statistics: {e.message}", err=True)
        raise typer.Exit(1)

    output_format = _get_output_format(config, json_output, table_output)

    if output_format == "json" or json_output:
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table(response, "Organisation Statistics")
        else:
            _print_json(response)


@stats_app.command("tags")
def tag_stats(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Get tag statistics."""
    from misp_cli.cli.app import get_app
    from misp_cli.core.exceptions import MISPAPIError, MISPNotFoundError

    app = get_app()
    config = app.profile
    client = app.client

    try:
        response = client.get_sync("/users/statistics/tags.json")
    except MISPNotFoundError as e:
        typer.echo(f"Error: Tag statistics endpoint not found. Check your MISP version.", err=True)
        raise typer.Exit(1)
    except MISPAPIError as e:
        typer.echo(f"Error fetching tag statistics: {e.message}", err=True)
        raise typer.Exit(1)

    output_format = _get_output_format(config, json_output, table_output)

    if output_format == "json" or json_output:
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table(response, "Tag Statistics")
        else:
            _print_json(response)
