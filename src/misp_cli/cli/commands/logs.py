"""Logs management commands for MISP CLI."""

from datetime import datetime
from typing import Any

import typer

from misp_cli.cli.output import get_output_format, print_csv, print_json, print_table

logs_app = typer.Typer(
    name="logs",
    help="View MISP logs",
    add_help_option=True,
    invoke_without_command=True,
)


@logs_app.callback()
def logs_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """View MISP logs."""
    if help:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@logs_app.command("list")
def list_logs(
    limit: int = typer.Option(100, "-l", "--limit", help="Maximum number of log entries"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """List system logs."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    params: dict[str, Any] = {
        "limit": limit,
        "page": page,
    }

    response = client.get_sync("/logs/index", params=params)

    output_format = get_output_format(config, json_output, table_output, csv_output)
    logs = response.get("logs", response.get("data", []))

    if output_format == "csv":
        print_csv(logs)
    elif output_format == "table":
        print_table(logs)
    else:
        print_json(logs)


@logs_app.command("search")
def search_logs(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(100, "-l", "--limit", help="Maximum number of results"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """Search system logs."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    params: dict[str, Any] = {
        "search": query,
        "limit": limit,
    }

    response = client.get_sync("/logs/search", params=params)

    output_format = get_output_format(config, json_output, table_output, csv_output)
    logs = response.get("logs", response.get("data", []))

    if output_format == "csv":
        print_csv(logs)
    elif output_format == "table":
        print_table(logs)
    else:
        print_json(logs)


@logs_app.command("user")
def user_logs(
    user_id: int = typer.Argument(..., help="User ID"),
    limit: int = typer.Option(100, "-l", "--limit", help="Maximum number of results"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """Get logs for a specific user."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    params: dict[str, Any] = {
        "user_id": user_id,
        "limit": limit,
    }

    response = client.get_sync(f"/logs/user/{user_id}", params=params)

    output_format = get_output_format(config, json_output, table_output, csv_output)
    logs = response.get("logs", response.get("data", []))

    if output_format == "csv":
        print_csv(logs)
    elif output_format == "table":
        print_table(logs)
    else:
        print_json(logs)


@logs_app.command("event")
def event_logs(
    event_id: int = typer.Argument(..., help="Event ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """Get logs for a specific event."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/logs/event/{event_id}")

    output_format = get_output_format(config, json_output, table_output, csv_output)
    logs = response.get("logs", response.get("data", []))

    if output_format == "csv":
        print_csv(logs)
    elif output_format == "table":
        print_table(logs)
    else:
        print_json(logs)


@logs_app.command("date")
def logs_by_date(
    date_str: str = typer.Argument(..., help="Date (YYYY-MM-DD)"),
    limit: int = typer.Option(100, "-l", "--limit", help="Maximum number of results"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """Get logs for a specific date."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        typer.echo("Error: Date must be in YYYY-MM-DD format", err=True)
        raise typer.Exit(1)

    params: dict[str, Any] = {
        "date": date_str,
        "limit": limit,
    }

    response = client.get_sync("/logs/date", params=params)

    output_format = get_output_format(config, json_output, table_output, csv_output)
    logs = response.get("logs", response.get("data", []))

    if output_format == "csv":
        print_csv(logs)
    elif output_format == "table":
        print_table(logs)
    else:
        print_json(logs)


@logs_app.command("clear")
def clear_logs(
    days: int = typer.Option(30, "-d", "--days", help="Clear logs older than N days"),
    force: bool = typer.Option(False, "-f", "--force", help="Force without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Clear old logs."""
    from misp_cli.cli.app import get_app

    if not force:
        typer.confirm(f"Are you sure you want to clear logs older than {days} days?", abort=True)

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync("/logs/clear", data={"days": days})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo("Logs cleared successfully")
