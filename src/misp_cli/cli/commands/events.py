"""Event management commands for MISP CLI."""

import json
from typing import Any

import typer
from rich.table import Table

from misp_cli.cli.output import print_csv, print_json
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


def _get_output_format(
    config: MISPProfile,
    json_output: bool,
    table_output: bool,
    csv_output: bool = False,
    format_option: str | None = None,
) -> str:
    """Determine output format based on options and config."""
    if csv_output:
        return "csv"
    if table_output:
        return "table"
    if json_output:
        return "json"
    if format_option:
        return format_option
    return config.output_format


def _print_table(data: list[dict], columns: list[str] | None = None) -> None:
    """Print data as a table with N/A for None values."""
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
            if value is None:
                row.append("N/A")
            elif isinstance(value, (dict, list)):
                row.append(str(len(value)))
            else:
                row.append(str(value))
        table.add_row(*row)

    console.print(table)


@events_app.command("list")
def list_events(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of events"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    search: str | None = typer.Option(None, "-s", "--search", help="Search query"),
    org: str | None = typer.Option(None, "-o", "--org", help="Organization filter"),
    from_date: str | None = typer.Option(
        None, "--from", help="Start date filter (e.g., 2024-03-19, 2024-03-19T11:10:24Z, 7d)"
    ),
    to_date: str | None = typer.Option(
        None, "--to", help="End date filter (e.g., 2024-03-19, 2024-03-19T11:10:24Z, 14d)"
    ),
    last: str | None = typer.Option(
        None, "--last", help="Relative time filter (e.g., 5d, 12h, 30m, 1617875568)"
    ),
    date: str | None = typer.Option(None, "--date", help="Event date filter (YYYY-MM-DD)"),
    timestamp: str | None = typer.Option(None, "--timestamp", help="Modification timestamp filter"),
    publish_timestamp: str | None = typer.Option(
        None, "--publish-timestamp", help="Publication timestamp filter"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
    format_option: str | None = typer.Option(
        None, "--format", help="Output format (json, table, csv)"
    ),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress non-essential output"),
):
    """List events with pagination and filtering."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    # Build query params similar to logs command
    params: dict[str, Any] = {}
    if limit:
        params["limit"] = limit
    if page:
        params["page"] = page
    if search:
        params["search"] = search
    if org:
        params["org"] = org

    # Check if filters that require restSearch are provided
    # The GET /events/index endpoint doesn't support org filtering, so we need restSearch
    has_date_filter = bool(from_date or to_date or last or date or timestamp or publish_timestamp)
    needs_rest_search = has_date_filter or org

    if needs_rest_search:
        # Use POST to /events/restSearch for date filtering
        # The MISP API requires date filters to be sent in the request body
        data: dict[str, Any] = {}
        if limit:
            data["limit"] = limit
        if page:
            data["page"] = page
        if search:
            data["search"] = search
        if org:
            data["org"] = org

        # Use the 'last' parameter directly - MISP handles relative time natively
        # This is more efficient than converting to from/to dates
        if last:
            data["last"] = last

        elif from_date:
            data["from"] = from_date
        if to_date:
            data["to"] = to_date
        if date:
            data["date"] = date
        if timestamp:
            data["timestamp"] = timestamp
        if publish_timestamp:
            data["publish_timestamp"] = publish_timestamp

        response = client.post_sync("/events/restSearch", data=data)
    else:
        # No date filters, use GET to /events/index
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        if date:
            params["date"] = date
        if timestamp:
            params["timestamp"] = timestamp
        if publish_timestamp:
            params["publish_timestamp"] = publish_timestamp

        response = client.get_sync("/events/index", params=params)

    output_format = _get_output_format(config, json_output, table_output, csv_output, format_option)

    # Unwrap nested Event structure: [{'Event': {...}}, ...] -> [{...}, ...]
    raw_events = response.get("events", response.get("data", response.get("response", [])))
    if raw_events and isinstance(raw_events, list):
        # Check if each item is wrapped in "Event" key
        if all(isinstance(item, dict) and "Event" in item for item in raw_events):
            events = [item["Event"] for item in raw_events]
        else:
            events = raw_events
    else:
        events = raw_events

    # Client-side limit fallback when API ignores pagination
    if limit and len(events) > limit:
        events = events[:limit]

    # Get pagination info from response
    total_count = response.get("total", len(events))

    if not quiet:
        typer.echo(f"Showing {len(events)} of {total_count} event(s)")

    if output_format == "csv":
        print_csv(events)
    elif output_format == "table":
        _print_table(events)
    else:
        print_json(events)


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
            print_json(response)
    else:
        print_json(response)


@events_app.command("create")
def create_event(
    info: str = typer.Option(..., "-i", "--info", help="Event info/title"),
    threat_level: int = typer.Option(
        2,
        "-t",
        "--threat-level",
        min=1,
        max=4,
        help="Threat level ID (1-4: 1=High, 2=Medium, 3=Low, 4=Undefined)",
    ),
    analysis: int = typer.Option(
        1,
        "-a",
        "--analysis",
        min=0,
        max=2,
        help="Analysis level (0=Initial, 1=Ongoing, 2=Completed)",
    ),
    distribution: int = typer.Option(
        1,
        "-d",
        "--distribution",
        min=0,
        max=5,
        help="Distribution (0=Your Organisation Only, 1=This Community Only, 2=Connected Communities, 3=All Communities, 4=Sharing Group, 5=Inherit From Event)",
    ),
    event_date: str | None = typer.Option(None, "-e", "--date", help="Event date (YYYY-MM-DD)"),
    org_id: int | None = typer.Option(
        None, "-o", "--org-id", help="Organisation ID to create event for"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress non-essential output"),
):
    """Create a new event in MISP."""
    from misp_cli.cli.app import get_app
    from misp_cli.core.exceptions import MISPAPIError

    app = get_app()
    config = app.profile
    client = app.client

    # Build event data structure for MISP API
    data: dict[str, Any] = {
        "info": info,
        "threat_level_id": threat_level,
        "analysis": analysis,
        "distribution": distribution,
    }

    if event_date:
        data["date"] = event_date

    if org_id:
        data["org_id"] = org_id

    try:
        response = client.post_sync("/events/add", data={"Event": data})

        if config.output_format == "json" or json_output:
            print_json(response)
        else:
            event_id = response.get("Event", {}).get("id", "Unknown")
            if not quiet:
                typer.echo(f"Event created successfully: {event_id}")
    except MISPAPIError as e:
        if "Event name required" in str(e.message) or "info" in str(e.message).lower():
            typer.echo("Error: Event info/title is required. Use --info or -i option.", err=True)
        elif "threat_level" in str(e.message).lower():
            typer.echo("Error: Invalid threat level. Must be 1-4.", err=True)
        else:
            typer.echo(f"Error creating event: {e.message}", err=True)
        raise typer.Exit(1) from None


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
        print_json(response)
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
        print_json(response)
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
        print_json(response)
    else:
        typer.echo(f"Event {event_id} unpublished successfully")


@events_app.command("search")
def search_events(
    term: str = typer.Argument(..., help="Search term"),
    from_date: str | None = typer.Option(
        None, "--from", help="Start date filter (e.g., 2024-03-19, 2024-03-19T11:10:24Z, 7d)"
    ),
    to_date: str | None = typer.Option(
        None, "--to", help="End date filter (e.g., 2024-03-19, 2024-03-19T11:10:24Z, 14d)"
    ),
    last: str | None = typer.Option(
        None, "--last", help="Relative time filter (e.g., 5d, 12h, 30m, 1617875568)"
    ),
    date: str | None = typer.Option(None, "--date", help="Event date filter (YYYY-MM-DD)"),
    timestamp: str | None = typer.Option(None, "--timestamp", help="Modification timestamp filter"),
    publish_timestamp: str | None = typer.Option(
        None, "--publish-timestamp", help="Publication timestamp filter"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Search for events."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    data: dict[str, Any] = {"search": term}
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

    # Unwrap nested Event structure: [{'Event': {...}}, ...] -> [{...}, ...]
    raw_events = response.get("events", response.get("data", response.get("response", [])))
    if raw_events and isinstance(raw_events, list):
        # Check if each item is wrapped in "Event" key
        if all(isinstance(item, dict) and "Event" in item for item in raw_events):
            events = [item["Event"] for item in raw_events]
        else:
            events = raw_events
    else:
        events = raw_events

    if output_format == "table":
        _print_table(events)
    else:
        print_json(events)


@events_app.command("export")
def export_event(
    event_id: int = typer.Argument(..., help="Event ID to export"),
    format: str = typer.Option(
        "json", "-f", "--format", help="Export format (json, csv, xml, striing, json2, rpz, misp2)"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress non-essential output"),
):
    """Export an event from MISP in the specified format."""
    from misp_cli.cli.app import get_app
    from misp_cli.core.exceptions import MISPAPIError

    app = get_app()
    config = app.profile
    client = app.client

    try:
        response = client.get_sync(f"/events/export/{event_id}", params={"format": format})

        if config.output_format == "json" or json_output:
            # If response is a dict, print as JSON; otherwise print raw
            if isinstance(response, dict):
                print_json(response)
            else:
                try:
                    print_json(json.loads(response))
                except (json.JSONDecodeError, TypeError):
                    print_json({"raw": response})
        else:
            if isinstance(response, dict):
                data = response.get("data", response)
                if isinstance(data, dict):
                    print_json(data)
                else:
                    typer.echo(str(data))
            else:
                typer.echo(str(response))
    except MISPAPIError as e:
        if e.status_code == 404:
            typer.echo(f"Error: Event {event_id} not found", err=True)
        elif e.status_code == 403:
            typer.echo(
                f"Error: Permission denied to export event {event_id}. Check your role permissions.",
                err=True,
            )
        else:
            typer.echo(f"Error exporting event: {e.message}", err=True)
        raise typer.Exit(1) from None


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
        print_json(attributes)
