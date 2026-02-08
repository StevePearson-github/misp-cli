"""Feed management functions for MISP CLI."""

import json
from typing import Any, Dict, List, Optional

import typer
from rich.table import Table

from misp_cli.core.config import MISPProfile

manage_feeds_app = typer.Typer(
    name="manage-feeds",
    help="Manage MISP feeds (ingestion and caching)",
    add_help_option=True,
    invoke_without_command=True,
)


@manage_feeds_app.callback()
def manage_feeds_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP feeds (ingestion and caching)."""
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


@manage_feeds_app.command("list")
def list_managed_feeds(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List all managed feeds."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync("/feeds/index")
    
    output_format = _get_output_format(config, json_output, table_output)
    feeds = response.get("feeds", response.get("data", []))
    
    if output_format == "table":
        _print_table(feeds)
    else:
        _print_json(feeds)


@manage_feeds_app.command("cache")
def cache_feed(
    feed_id: int = typer.Argument(..., help="Feed ID to cache"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Cache a feed locally."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/feeds/cache/{feed_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Feed {feed_id} cached successfully")


@manage_feeds_app.command("fetch")
def fetch_feed_data(
    feed_id: int = typer.Argument(..., help="Feed ID to fetch"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Fetch data from a feed."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/feeds/fetch/{feed_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Feed {feed_id} fetched successfully")


@manage_feeds_app.command("ingest")
def ingest_feed(
    feed_id: int = typer.Argument(..., help="Feed ID to ingest"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Ingest events from a feed."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/feeds/import/{feed_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Feed {feed_id} ingested successfully")


@manage_feeds_app.command("enable")
def enable_feed(
    feed_id: int = typer.Argument(..., help="Feed ID to enable"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Enable a feed."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(f"/feeds/enable/{feed_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Feed {feed_id} enabled successfully")


@manage_feeds_app.command("disable")
def disable_feed(
    feed_id: int = typer.Argument(..., help="Feed ID to disable"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Disable a feed."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(f"/feeds/disable/{feed_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Feed {feed_id} disabled successfully")


@manage_feeds_app.command("all-cache")
def cache_all_feeds(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Cache all enabled feeds."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync("/feeds/cacheAll")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo("All feeds cached successfully")


@manage_feeds_app.command("all-ingest")
def ingest_all_feeds(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Ingest events from all enabled feeds."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync("/feeds/importAll")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo("All feeds ingested successfully")


@manage_feeds_app.command("statistics")
def get_feed_statistics(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Get feed statistics."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync("/feeds/statistics")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        _print_json(response)
