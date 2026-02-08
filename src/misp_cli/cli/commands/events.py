"""Event management commands for MISP CLI."""

import json
from datetime import date
from typing import Any, Dict, List, Optional

import typer
from rich.table import Table

from misp_cli.core.config import MISPProfile

events_app = typer.Typer(
    name="events",
    help="Manage MISP events",
    add_help_option=True,
    invoke_without_command=True,
)


@events_app.callback()
def events_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP events."""
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
    
    # Add columns
    if columns:
        for col in columns:
            table.add_column(col.replace("_", " ").title())
    else:
        for key in data[0].keys():
            table.add_column(key.replace("_", " ").title())
    
    # Add rows
    for item in data:
        row = []
        for value in item.values():
            if isinstance(value, (dict, list)):
                row.append(str(len(value)))
            else:
                row.append(str(value))
        table.add_row(*row)
    
    console.print(table)


@events_app.command("list")
def list_events(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of events"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    search: Optional[str] = typer.Option(None, "-s", "--search", help="Search query"),
    org: Optional[str] = typer.Option(None, "-o", "--org", help="Organization filter"),
    from_date: Optional[str] = typer.Option(None, "--from", help="Start date filter (e.g., 2024-03-19, 2024-03-19T11:10:24Z, 7d)"),
    to_date: Optional[str] = typer.Option(None, "--to", help="End date filter (e.g., 2024-03-19, 2024-03-19T11:10:24Z, 14d)"),
    last: Optional[str] = typer.Option(None, "--last", help="Relative time filter (e.g., 5d, 12h, 30m, 1617875568)"),
    date: Optional[str] = typer.Option(None, "--date", help="Event date filter (YYYY-MM-DD)"),
    timestamp: Optional[str] = typer.Option(None, "--timestamp", help="Modification timestamp filter"),
    publish_timestamp: Optional[str] = typer.Option(None, "--publish-timestamp", help="Publication timestamp filter"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List events with pagination and filtering."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    params: Dict[str, Any] = {
        "limit": limit,
        "page": page,
    }
    if search:
        params["search"] = search
    if org:
        params["org"] = org
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    if last:
        params["last"] = last
    if date:
        params["date"] = date
    if timestamp:
        params["timestamp"] = timestamp
    if publish_timestamp:
        params["publish_timestamp"] = publish_timestamp
    
    response = client.get_sync("/events/index", params=params)
    
    output_format = _get_output_format(config, json_output, table_output)
    events = response.get("events", response.get("data", []))
    
    if output_format == "table":
        _print_table(events)
    else:
        _print_json(events)


@events_app.command("show")
def show_event(
    event_id: int = typer.Argument(..., help="Event ID to show"),
    context: bool = typer.Option(False, "-c", "--context", help="Include context"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Show details of a specific event."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    params = {"context": 1} if context else {}
    response = client.get_sync(f"/events/view/{event_id}", params=params)
    
    output_format = _get_output_format(config, json_output, table_output)
    
    if output_format == "table":
        if isinstance(response, dict):
            _print_table([response])
        else:
            _print_json(response)
    else:
        _print_json(response)


@events_app.command("create")
def create_event(
    info: str = typer.Option(..., "-i", "--info", help="Event info"),
    threat_level: int = typer.Option(2, "-t", "--threat-level", min=1, max=4, help="Threat level (1-4)"),
    analysis: int = typer.Option(1, "-a", "--analysis", min=0, max=2, help="Analysis level (0-2)"),
    distribution: int = typer.Option(5, "-d", "--distribution", min=0, max=5, help="Distribution (0-5)"),
    event_date: Optional[str] = typer.Option(None, "-e", "--date", help="Event date (YYYY-MM-DD)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Create a new event."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    data: Dict[str, Any] = {
        "info": info,
        "threat_level_id": threat_level,
        "analysis": analysis,
        "distribution": distribution,
    }
    
    if event_date:
        data["date"] = event_date
    
    response = client.post_sync("/events/add", data={"Event": data})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Event created successfully: {response.get('Event', {}).get('id', 'Unknown')}")


@events_app.command("delete")
def delete_event(
    event_id: int = typer.Argument(..., help="Event ID to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Force deletion without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Delete an event."""
    from misp_cli.cli.app import get_app
    
    if not force:
        typer.confirm(f"Are you sure you want to delete event {event_id}?", abort=True)
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(f"/events/delete/{event_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Event {event_id} deleted successfully")


@events_app.command("publish")
def publish_event(
    event_id: int = typer.Argument(..., help="Event ID to publish"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Publish an event."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(f"/events/publish/{event_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Event {event_id} published successfully")


@events_app.command("unpublish")
def unpublish_event(
    event_id: int = typer.Argument(..., help="Event ID to unpublish"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Unpublish an event."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(f"/events/unpublish/{event_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Event {event_id} unpublished successfully")


@events_app.command("search")
def search_events(
    term: str = typer.Argument(..., help="Search term"),
    from_date: Optional[str] = typer.Option(None, "--from", help="Start date filter (e.g., 2024-03-19, 2024-03-19T11:10:24Z, 7d)"),
    to_date: Optional[str] = typer.Option(None, "--to", help="End date filter (e.g., 2024-03-19, 2024-03-19T11:10:24Z, 14d)"),
    last: Optional[str] = typer.Option(None, "--last", help="Relative time filter (e.g., 5d, 12h, 30m, 1617875568)"),
    date: Optional[str] = typer.Option(None, "--date", help="Event date filter (YYYY-MM-DD)"),
    timestamp: Optional[str] = typer.Option(None, "--timestamp", help="Modification timestamp filter"),
    publish_timestamp: Optional[str] = typer.Option(None, "--publish-timestamp", help="Publication timestamp filter"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Search for events."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    data: Dict[str, Any] = {"search": term}
    if from_date:
        data["from"] = from_date
    if to_date:
        data["to"] = to_date
    if last:
        data["last"] = last
    if date:
        data["date"] = date
    if timestamp:
        data["timestamp"] = timestamp
    if publish_timestamp:
        data["publish_timestamp"] = publish_timestamp
    
    response = client.post_sync("/events/restSearch", data=data)
    
    output_format = _get_output_format(config, json_output, table_output)
    events = response.get("events", response.get("data", []))
    
    if output_format == "table":
        _print_table(events)
    else:
        _print_json(events)


@events_app.command("export")
def export_event(
    event_id: int = typer.Argument(..., help="Event ID to export"),
    format: str = typer.Option("json", "-f", "--format", help="Export format (json, csv, xml)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Export an event."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/events/export/{event_id}", params={"format": format})
    
    if format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(response.get("data", response))


@events_app.command("attributes")
def list_event_attributes(
    event_id: int = typer.Argument(..., help="Event ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List attributes of an event."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/events/view/{event_id}", params={"includeAttributes": 1})
    
    output_format = _get_output_format(config, json_output, table_output)
    event = response.get("Event", response)
    attributes = event.get("Attribute", [])
    
    if output_format == "table":
        _print_table(attributes)
    else:
        _print_json(attributes)
