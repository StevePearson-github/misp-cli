"""Event blocklist management commands for MISP CLI."""

from typing import Any

import typer

from misp_cli.cli.output import (
    COUNT_OPTION,
    get_output_format,
    print_count,
    print_csv,
    print_json,
    print_table,
)

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
    # Show help if requested or no subcommand given
    if help or ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


@event_blocklists_app.command("list")
def list_event_blocklists(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of entries"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
    count: bool = COUNT_OPTION,
):
    """List all event blocklist entries."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    effective_limit = 0 if count is True else limit
    params: dict[str, Any] = {"page": page}
    if effective_limit:
        params["limit"] = effective_limit

    response = client.get_sync("/eventBlocklists/index", params=params)

    output_format = get_output_format(config, json_output, table_output, csv_output)
    blocklists = response.get("eventBlocklists", response.get("data", []))

    if count is True:
        print_count(blocklists, json_output)

    if output_format == "csv":
        print_csv(blocklists)
    elif output_format == "table":
        print_table(blocklists)
    else:
        print_json(blocklists)


@event_blocklists_app.command("add-uuid")
def add_event_blocklist_uuid(
    uuid: str = typer.Argument(..., help="Event UUID to block"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Add an event to the blocklist by UUID."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    data: dict[str, Any] = {
        "event_uuid": uuid,
    }

    response = client.post_sync("/eventBlocklists/add", data={"EventBlocklist": data})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        blocklist_id = response.get("EventBlocklist", {}).get("id", "Unknown")
        typer.echo(f"Event blocklist entry created: {blocklist_id}")


@event_blocklists_app.command("remove")
def remove_event_blocklist(
    blocklist_id: int = typer.Argument(..., help="Blocklist entry ID to remove"),
    force: bool = typer.Option(False, "-f", "--force", help="Force without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Remove an event from the blocklist."""
    from misp_cli.cli.app import get_app

    if not force:
        typer.confirm(
            f"Are you sure you want to remove blocklist entry {blocklist_id}?", abort=True
        )

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/eventBlocklists/delete/{blocklist_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Blocklist entry {blocklist_id} removed successfully")


@event_blocklists_app.command("bulk-add")
def bulk_add_event_blocklist(
    file_path: str = typer.Argument(..., help="Path to file with event info or IDs (one per line)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Bulk add events to the blocklist from a file."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    try:
        with open(file_path) as f:
            values = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        typer.echo(f"Error: File {file_path} not found", err=True)
        raise typer.Exit(1) from None

    data: dict[str, Any] = {
        "values": "\n".join(values),
    }

    response = client.post_sync("/eventBlocklists/bulkAdd", data={"EventBlocklist": data})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        added = response.get("added", 0)
        typer.echo(f"Added {added} events to blocklist")


@event_blocklists_app.command("cleanup")
def cleanup_event_blocklists(
    force: bool = typer.Option(False, "-f", "--force", help="Force without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Remove blocklist entries for events that no longer exist."""
    from misp_cli.cli.app import get_app

    if not force:
        typer.confirm("Are you sure you want to cleanup blocklist entries?", abort=True)

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync("/eventBlocklists/cleanup")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        removed = response.get("removed", 0)
        typer.echo(f"Removed {removed} stale blocklist entries")
