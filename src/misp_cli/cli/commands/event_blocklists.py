"""Event blocklist management commands for MISP CLI."""

import json
from typing import Any, Dict, List, Optional

import typer
from rich.table import Table

from misp_cli.core.config import MISPProfile

event_blocklists_app = typer.Typer(
    name="event-blocklists",
    help="Manage MISP event blocklists",
    add_help_option=True,
    invoke_without_command=True,
)


@event_blocklists_app.callback()
def event_blocklists_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP event blocklists."""
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
        for key in data[0].keys():
            table.add_column(key.replace("_", " ").title())
    
    for item in data:
        row = []
        for value in item.values():
            if isinstance(value, (dict, list)):
                row.append(str(len(value)))
            else:
                row.append(str(value))
        table.add_row(*row)
    
    console.print(table)


@event_blocklists_app.command("list")
def list_blocklist(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of entries"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List all event blocklist entries."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    params: Dict[str, Any] = {
        "limit": limit,
        "page": page,
    }
    
    response = client.get_sync("/eventBlocklists/index", params=params)
    
    output_format = _get_output_format(config, json_output, table_output)
    entries = response.get("eventBlocklists", response.get("data", []))
    
    if output_format == "table":
        _print_table(entries)
    else:
        _print_json(entries)


@event_blocklists_app.command("add")
def add_to_blocklist(
    event_id: int = typer.Argument(..., help="Event ID to block"),
    comment: Optional[str] = typer.Option(None, "-c", "--comment", help="Comment"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Add an event to the blocklist."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    data: Dict[str, Any] = {
        "event_id": event_id,
    }
    if comment:
        data["comment"] = comment
    
    response = client.post_sync("/eventBlocklists/add", data={"EventBlocklist": data})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        entry_id = response.get("EventBlocklist", {}).get("id", "Unknown")
        typer.echo(f"Event {event_id} added to blocklist: {entry_id}")


@event_blocklists_app.command("delete")
def remove_from_blocklist(
    entry_id: int = typer.Argument(..., help="Blocklist entry ID to remove"),
    force: bool = typer.Option(False, "-f", "--force", help="Force deletion without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Remove an entry from the blocklist."""
    from misp_cli.cli.app import get_app
    
    if not force:
        typer.confirm(f"Are you sure you want to remove blocklist entry {entry_id}?", abort=True)
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(f"/eventBlocklists/delete/{entry_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Blocklist entry {entry_id} removed successfully")


@event_blocklists_app.command("check")
def check_event(
    event_id: int = typer.Argument(..., help="Event ID to check"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Check if an event is blocklisted."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync("/eventBlocklists/check", params={"event_id": event_id})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        result = response.get("EventBlocklist", {})
        if result.get("blocked"):
            typer.echo(f"Event {event_id} is BLOCKED: {result.get('comment', '')}")
        else:
            typer.echo(f"Event {event_id} is not blocklisted")
