"""Feed management commands for MISP CLI."""

from typing import Any

import typer

from misp_cli.cli.output import get_output_format, print_csv, print_json, print_table, unwrap_nested_data

manage_feeds_app = typer.Typer(
    name="feeds",
    help="Manage MISP feeds",
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
    """Manage MISP feeds."""
    if help:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@manage_feeds_app.command("list")
def list_feeds(
    enabled: bool = typer.Option(False, "-e", "--enabled", help="Show only enabled feeds"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """List all feeds."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    params: dict[str, Any] = {}
    if enabled:
        params["enabled"] = "true"

    response = client.get_sync("/feeds/index", params=params)

    output_format = get_output_format(config, json_output, table_output, csv_output)
    feeds = unwrap_nested_data(response, "Feed")

    if output_format == "csv":
        print_csv(feeds)
    elif output_format == "table":
        print_table(feeds)
    else:
        print_json(feeds)


@manage_feeds_app.command("show")
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
            print_table([response])
        else:
            print_json(response)


@manage_feeds_app.command("create")
def create_feed(
    name: str = typer.Option(..., "-n", "--name", help="Feed name"),
    url: str = typer.Option(..., "-u", "--url", help="Feed URL"),
    provider: str = typer.Option(..., "-p", "--provider", help="Feed provider"),
    enabled: bool = typer.Option(False, "-e", "--enabled", help="Enable feed after creation"),
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
        "enabled": enabled,
    }

    response = client.post_sync("/feeds/add", data={"Feed": data})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        feed_id = response.get("Feed", {}).get("id", "Unknown")
        typer.echo(f"Feed created successfully: {feed_id}")


@manage_feeds_app.command("edit")
def edit_feed(
    feed_id: int = typer.Argument(..., help="Feed ID to edit"),
    name: str | None = typer.Option(None, "-n", "--name", help="New name"),
    url: str | None = typer.Option(None, "-u", "--url", help="New URL"),
    provider: str | None = typer.Option(None, "-p", "--provider", help="New provider"),
    enabled: bool | None = typer.Option(None, "-e", "--enabled", help="Enable/disable feed"),
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


@manage_feeds_app.command("delete")
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
        print_json(response)
    else:
        typer.echo(f"Feed {feed_id} enabled")


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
        print_json(response)
    else:
        typer.echo(f"Feed {feed_id} disabled")


@manage_feeds_app.command("fetch")
def fetch_feed(
    feed_id: int = typer.Argument(..., help="Feed ID to fetch"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Fetch events from a feed."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/feeds/fetch/{feed_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Feed {feed_id} fetched successfully")


@manage_feeds_app.command("cache")
def cache_feed(
    feed_id: int = typer.Argument(..., help="Feed ID to cache"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Cache a feed."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/feeds/cache/{feed_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Feed {feed_id} cached successfully")


@manage_feeds_app.command("test")
def test_feed(
    feed_id: int = typer.Argument(..., help="Feed ID to test"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Test a feed connection."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/feeds/test/{feed_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        result = response.get("Feed", {})
        status = result.get("status", "unknown")
        if status == "OK":
            typer.echo(f"Feed {feed_id} test: SUCCESS")
        else:
            typer.echo(f"Feed {feed_id} test: {status}")


@manage_feeds_app.command("import")
def import_feed(
    file_path: str = typer.Argument(..., help="Path to feed JSON file"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Import a feed from a JSON file."""
    import json

    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    try:
        with open(file_path) as f:
            feed_data = json.load(f)
    except FileNotFoundError:
        typer.echo(f"Error: File {file_path} not found", err=True)
        raise typer.Exit(1)
    except json.JSONDecodeError:
        typer.echo(f"Error: Invalid JSON in {file_path}", err=True)
        raise typer.Exit(1)

    response = client.post_sync("/feeds/import", data={"Feed": feed_data})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        feed_id = response.get("Feed", {}).get("id", "Unknown")
        typer.echo(f"Feed imported successfully: {feed_id}")


@manage_feeds_app.command("export")
def export_feed(
    feed_id: int = typer.Argument(..., help="Feed ID to export"),
    output_file: str | None = typer.Option(None, "-o", "--output", help="Output file path"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Export a feed to a JSON file."""
    import json

    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/feeds/export/{feed_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    elif output_file:
        with open(output_file, "w") as f:
            json.dump(response, f, indent=2)
        typer.echo(f"Exported to {output_file}")
    else:
        print_json(response)
