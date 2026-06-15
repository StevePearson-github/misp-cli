"""Logs management commands for MISP CLI."""

from datetime import datetime
from typing import Any

import typer

from misp_cli.cli.output import (
    COUNT_OPTION,
    get_output_format,
    print_count,
    print_csv,
    print_json,
    print_table,
    unwrap_nested_data,
)

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
    # Show help if requested or no subcommand given
    if help or ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


@logs_app.command("list")
def list_logs(
    limit: int = typer.Option(100, "-l", "--limit", help="Maximum number of log entries"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    email: str | None = typer.Option(None, "-e", "--email", help="Filter by email address"),
    model: str | None = typer.Option(
        None, "--model", help="Filter by model (e.g., User, Event, Attribute)"
    ),
    action: str | None = typer.Option(
        None, "--action", help="Filter by action (e.g., login, logout, add, edit)"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
    count: bool = COUNT_OPTION,
):
    """List system logs."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    effective_limit = 0 if count is True else limit

    # Use POST to /admin/logs when any filter that requires it is provided
    if email or model or action:
        data: dict[str, Any] = {
            "page": page,
            "sort": "Log.id",
            "direction": "asc",
        }
        if effective_limit:
            data["limit"] = effective_limit
        if email:
            data["email"] = email
        if model:
            data["model"] = model
        if action:
            data["action"] = action
        response = client.post_sync("/logs/index/sort:Log.id/direction:asc", data=data)
    else:
        response = client.get_sync(
            f"/logs/admin_index/limit:{effective_limit}/sort:Log.id/direction:desc"
        )

    output_format = get_output_format(config, json_output, table_output, csv_output)
    logs = unwrap_nested_data(response, "Log")

    if count is True:
        print_count(logs, json_output)
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
    count: bool = COUNT_OPTION,
):
    """Search system logs."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    effective_limit = 0 if count is True else limit
    data: dict[str, Any] = {"search": query}
    if effective_limit:
        data["limit"] = effective_limit

    response = client.post_sync("/logs/index/sort:Log.id/direction:asc", data=data)

    output_format = get_output_format(config, json_output, table_output, csv_output)
    logs = unwrap_nested_data(response, "Log")

    if count is True:
        print_count(logs, json_output)
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
    count: bool = COUNT_OPTION,
):
    """Get logs for a specific user."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    effective_limit = 0 if count is True else limit
    data: dict[str, Any] = {"model": "User", "model_id": user_id}
    if effective_limit:
        data["limit"] = effective_limit

    response = client.post_sync("/logs/index/sort:Log.id/direction:desc", data=data)

    output_format = get_output_format(config, json_output, table_output, csv_output)
    logs = unwrap_nested_data(response, "Log")

    if count is True:
        print_count(logs, json_output)
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
    count: bool = COUNT_OPTION,
):
    """Get logs for a specific event."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    data: dict[str, Any] = {"model": "Event", "model_id": event_id}

    response = client.post_sync("/logs/index/sort:Log.id/direction:desc", data=data)

    output_format = get_output_format(config, json_output, table_output, csv_output)
    logs = unwrap_nested_data(response, "Log")

    if count is True:
        print_count(logs, json_output)
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
    count: bool = COUNT_OPTION,
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
        raise typer.Exit(1) from None

    effective_limit = 0 if count is True else limit
    data: dict[str, Any] = {"from": date_str, "to": date_str}
    if effective_limit:
        data["limit"] = effective_limit

    response = client.post_sync("/logs/index/sort:Log.id/direction:asc", data=data)

    output_format = get_output_format(config, json_output, table_output, csv_output)
    logs = unwrap_nested_data(response, "Log")

    if count is True:
        print_count(logs, json_output)
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
