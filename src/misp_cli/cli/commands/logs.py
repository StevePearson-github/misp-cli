"""Logs management commands for MISP CLI."""

import json
from typing import Any, Dict, List, Optional

import typer
from rich.table import Table

from misp_cli.core.config import MISPProfile

logs_app = typer.Typer(
    name="logs",
    help="Manage MISP logs",
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
    """Manage MISP logs."""
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


def _print_table(data: List[Dict], columns: Optional[List[str]] = None) -> None:
    """Print data as a table."""
    if not data:
        typer.echo("No data available")
        return

    from misp_cli.cli.app import get_app
    console = get_app().console
    table = Table(show_header=True, header_style="bold magenta")

    if columns:
        for col in columns:
            table.add_column(col.replace("_", " ").title())
    else:
        # Use common log fields
        common_fields = ["id", "title", "created", "model", "action", "user_id", "email", "org", "ip"]
        for key in common_fields:
            if data and key in data[0]:
                table.add_column(key.replace("_", " ").title())
        # Add any other fields
        if data:
            for key in data[0].keys():
                if key not in common_fields:
                    table.add_column(key.replace("_", " ").title())

    for item in data:
        row = []
        for col in table.columns:
            col_name = col.header.lower().replace(" ", "_")
            value = item.get(col_name, "")
            if isinstance(value, (dict, list)):
                row.append(str(len(value)))
            else:
                row.append(str(value)[:50] if value else "")
        table.add_row(*row)

    console.print(table)


@logs_app.command("list")
def list_logs(
    ctx: typer.Context,
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of logs to return"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    model: Optional[str] = typer.Option(None, "-m", "--model", help="Filter by model"),
    action: Optional[str] = typer.Option(None, "-a", "--action", help="Filter by action"),
    user_id: Optional[str] = typer.Option(None, "-u", "--user-id", help="Filter by user ID"),
    email: Optional[str] = typer.Option(None, "-e", "--email", help="Filter by email"),
    org: Optional[str] = typer.Option(None, "-o", "--org", help="Filter by organisation"),
    ip: Optional[str] = typer.Option(None, "-i", "--ip", help="Filter by IP address"),
    title: Optional[str] = typer.Option(None, "-t", "--title", help="Filter by title"),
    json_output: bool = typer.Option(False, "-j", "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-T", "--table", help="Output as table"),
):
    """List MISP logs with optional filters."""
    from misp_cli.cli.app import get_app
    from misp_cli.core.exceptions import MISPAPIError, MISPNotFoundError

    app = get_app()
    config = app.profile
    client = app.client

    params: Dict[str, Any] = {
        "limit": limit,
        "page": page,
    }

    # Add optional filters
    if model:
        params["model"] = model
    if action:
        params["action"] = action
    if user_id:
        params["user_id"] = user_id
    if email:
        params["email"] = email
    if org:
        params["org"] = org
    if ip:
        params["ip"] = ip
    if title:
        params["title"] = title

    try:
        response = client.post_sync("/admin/logs", data=params)
    except MISPNotFoundError as e:
        typer.echo(f"Error: Logs endpoint not found. Check your MISP version or permissions.", err=True)
        raise typer.Exit(1)
    except MISPAPIError as e:
        typer.echo(f"Error fetching logs: {e.message}", err=True)
        raise typer.Exit(1)

    output_format = _get_output_format(config, json_output, table_output)

    # Handle response - logs are returned as an array in the response
    if isinstance(response, list):
        logs = response
    elif isinstance(response, dict):
        logs = response.get("Log", response.get("logs", response.get("data", response.get("response", []))))
    else:
        logs = []

    if output_format == "table":
        _print_table(logs)
    else:
        _print_json(logs)


@logs_app.command("search")
def search_logs(
    ctx: typer.Context,
    query: str = typer.Argument(..., help="Search term to match against log titles or descriptions"),
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of logs to return"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "-j", "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-T", "--table", help="Output as table"),
):
    """Search logs by title or description."""
    from misp_cli.cli.app import get_app
    from misp_cli.core.exceptions import MISPAPIError, MISPNotFoundError

    app = get_app()
    config = app.profile
    client = app.client

    params: Dict[str, Any] = {
        "limit": limit,
        "page": page,
        "title": query,
    }

    try:
        response = client.post_sync("/admin/logs", data=params)
    except MISPNotFoundError as e:
        typer.echo(f"Error: Logs endpoint not found. Check your MISP version or permissions.", err=True)
        raise typer.Exit(1)
    except MISPAPIError as e:
        typer.echo(f"Error searching logs: {e.message}", err=True)
        raise typer.Exit(1)

    output_format = _get_output_format(config, json_output, table_output)

    if isinstance(response, list):
        logs = response
    elif isinstance(response, dict):
        logs = response.get("Log", response.get("logs", response.get("data", response.get("response", []))))
    else:
        logs = []

    if output_format == "table":
        _print_table(logs)
    else:
        _print_json(logs)


@logs_app.command("user")
def user_logs(
    ctx: typer.Context,
    user_id: int = typer.Argument(..., help="User ID to filter logs"),
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of logs to return"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "-j", "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-T", "--table", help="Output as table"),
):
    """Get logs for a specific user."""
    from misp_cli.cli.app import get_app
    from misp_cli.core.exceptions import MISPAPIError, MISPNotFoundError

    app = get_app()
    config = app.profile
    client = app.client

    params: Dict[str, Any] = {
        "limit": limit,
        "page": page,
        "user_id": str(user_id),
    }

    try:
        response = client.post_sync("/admin/logs", data=params)
    except MISPNotFoundError as e:
        typer.echo(f"Error: Logs endpoint not found. Check your MISP version or permissions.", err=True)
        raise typer.Exit(1)
    except MISPAPIError as e:
        typer.echo(f"Error fetching user logs: {e.message}", err=True)
        raise typer.Exit(1)

    output_format = _get_output_format(config, json_output, table_output)

    if isinstance(response, list):
        logs = response
    elif isinstance(response, dict):
        logs = response.get("Log", response.get("logs", response.get("data", response.get("response", []))))
    else:
        logs = []

    if output_format == "table":
        _print_table(logs)
    else:
        _print_json(logs)


@logs_app.command("model")
def model_logs(
    ctx: typer.Context,
    model: str = typer.Argument(..., help="Model name to filter logs (e.g., Event, Attribute, User)"),
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of logs to return"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "-j", "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-T", "--table", help="Output as table"),
):
    """Get logs for a specific model type."""
    from misp_cli.cli.app import get_app
    from misp_cli.core.exceptions import MISPAPIError, MISPNotFoundError

    app = get_app()
    config = app.profile
    client = app.client

    params: Dict[str, Any] = {
        "limit": limit,
        "page": page,
        "model": model,
    }

    try:
        response = client.post_sync("/admin/logs", data=params)
    except MISPNotFoundError as e:
        typer.echo(f"Error: Logs endpoint not found. Check your MISP version or permissions.", err=True)
        raise typer.Exit(1)
    except MISPAPIError as e:
        typer.echo(f"Error fetching model logs: {e.message}", err=True)
        raise typer.Exit(1)

    output_format = _get_output_format(config, json_output, table_output)

    if isinstance(response, list):
        logs = response
    elif isinstance(response, dict):
        logs = response.get("Log", response.get("logs", response.get("data", response.get("response", []))))
    else:
        logs = []

    if output_format == "table":
        _print_table(logs)
    else:
        _print_json(logs)
