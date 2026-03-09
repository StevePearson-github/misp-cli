"""Feed management commands for MISP CLI."""

from typing import Any

import typer
from rich.table import Table

from misp_cli.cli.output import get_output_format, print_csv, print_json

feeds_app = typer.Typer(
    name="feeds",
    help="Manage MISP feeds",
    add_help_option=True,
    invoke_without_command=True,
)


@feeds_app.callback()
def feeds_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP feeds."""
    # Show help if requested or no subcommand given
    if help or ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


def _print_table(data: list[dict], columns: list[str] | None = None) -> None:
    """Print data as a table with N/A for None values."""
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
            if value is None:
                row.append("N/A")
            elif isinstance(value, (dict, list)):
                row.append(str(len(value)))
            else:
                row.append(str(value))
        table.add_row(*row)

    console.print(table)


@feeds_app.command("list")
def list_feeds(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of feeds"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    enabled_only: bool = typer.Option(False, "--enabled", help="Show only enabled feeds"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress non-essential output"),
):
    """List all feeds."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    params: dict[str, Any] = {
        "limit": limit,
        "page": page,
    }
    if enabled_only:
        params["enabled"] = 1

    response = client.get_sync("/feeds/index", params=params)

    output_format = get_output_format(config, json_output, table_output, csv_output)

    # Unwrap nested Feed structure: [{'Feed': {...}}, ...] -> [{...}, ...]
    raw_feeds = response.get("feeds", response.get("data", []))
    if raw_feeds and isinstance(raw_feeds, list):
        # Check if each item is wrapped in "Feed" key
        if all(isinstance(item, dict) and "Feed" in item for item in raw_feeds):
            feeds = [item["Feed"] for item in raw_feeds]
        else:
            feeds = raw_feeds
    else:
        feeds = raw_feeds

    if not quiet:
        typer.echo(f"Found {len(feeds)} feed(s)")

    if output_format == "csv":
        print_csv(feeds)
    elif output_format == "table":
        _print_table(feeds)
    else:
        print_json(feeds)


@feeds_app.command("show")
def show_feed(
    feed_id: int = typer.Argument(..., help="Feed ID to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific feed."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/feeds/view/{feed_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            print_json(response)


@feeds_app.command("create")
def create_feed(
    name: str = typer.Option(..., "-n", "--name", help="Feed name"),
    url: str = typer.Option(..., "-u", "--url", help="Feed URL"),
    provider: str = typer.Option(..., "-p", "--provider", help="Provider name"),
    format_type: str = typer.Option(
        "misp", "-f", "--format", help="Feed format (misp, freetext, csv)"
    ),
    enabled: bool = typer.Option(False, "--enabled", help="Enable feed after creation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Create a new feed."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    data: dict[str, Any] = {
        "name": name,
        "url": url,
        "provider": provider,
        "source_format": format_type,
        "enabled": enabled,
    }

    response = client.post_sync("/feeds/add", data={"Feed": data})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        feed_id = response.get("Feed", {}).get("id", "Unknown")
        typer.echo(f"Feed created successfully: {feed_id}")


@feeds_app.command("edit")
def edit_feed(
    feed_id: int = typer.Argument(..., help="Feed ID to edit"),
    name: str | None = typer.Option(None, "-n", "--name", help="New name"),
    url: str | None = typer.Option(None, "-u", "--url", help="New URL"),
    provider: str | None = typer.Option(None, "-p", "--provider", help="New provider"),
    enabled: bool | None = typer.Option(None, "--enabled", help="Enable/disable feed"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Edit a feed."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    data: dict[str, Any] = {}
    if name:
        data["name"] = name
    if url:
        data["url"] = url
    if provider:
        data["provider"] = provider
    if enabled is not None:
        data["enabled"] = enabled

    if not data:
        typer.echo("No changes specified", err=True)
        raise typer.Exit(1)

    response = client.post_sync(f"/feeds/edit/{feed_id}", data={"Feed": data})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Feed {feed_id} updated successfully")


@feeds_app.command("delete")
def delete_feed(
    feed_id: int = typer.Argument(..., help="Feed ID to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Force deletion without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Delete a feed."""
    from misp_cli.cli.app import get_app

    if not force:
        typer.confirm(f"Are you sure you want to delete feed {feed_id}?", abort=True)

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/feeds/delete/{feed_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Feed {feed_id} deleted successfully")


@feeds_app.command("fetch")
def fetch_feed(
    feed_id: int = typer.Argument(..., help="Feed ID to fetch"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Fetch events from a feed."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/feeds/fetch/{feed_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Feed {feed_id} fetched successfully")


@feeds_app.command("cache")
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
        print_json(response)
    else:
        typer.echo(f"Feed {feed_id} cached successfully")


@feeds_app.command("enable")
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
        print_json(response)
    else:
        typer.echo(f"Feed {feed_id} enabled successfully")


@feeds_app.command("disable")
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
        print_json(response)
    else:
        typer.echo(f"Feed {feed_id} disabled successfully")


@feeds_app.command("import")
def import_feed(
    feed_id: int = typer.Argument(..., help="Feed ID to import from"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Import events from a feed."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/feeds/import/{feed_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Events imported from feed {feed_id} successfully")


@feeds_app.command("test")
def test_feed(
    feed_id: int = typer.Argument(..., help="Feed ID to test"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Test a feed connection."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/feeds/test/{feed_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        result = response.get("Feed", {}).get("test", {})
        if result.get("status") == "OK":
            typer.echo(f"Feed {feed_id} test: SUCCESS")
        else:
            typer.echo(f"Feed {feed_id} test: FAILED")
