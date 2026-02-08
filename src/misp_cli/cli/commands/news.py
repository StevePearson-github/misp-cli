"""News feed management commands for MISP CLI."""

from typing import Any

import typer

from misp_cli.cli.output import get_output_format, print_csv, print_json, print_table

news_app = typer.Typer(
    name="news",
    help="Manage MISP news feeds",
    add_help_option=True,
    invoke_without_command=True,
)


@news_app.callback()
def news_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP news feeds."""
    if help:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@news_app.command("list")
def list_news(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of news items"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """List all news items."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    params: dict[str, Any] = {
        "limit": limit,
    }

    response = client.get_sync("/news/index", params=params)

    output_format = get_output_format(config, json_output, table_output, csv_output)
    news_items = response.get("news", response.get("data", []))

    if output_format == "csv":
        print_csv(news_items)
    elif output_format == "table":
        print_table(news_items)
    else:
        print_json(news_items)


@news_app.command("show")
def show_news(
    news_id: int = typer.Argument(..., help="News ID to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific news item."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/news/view/{news_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        if isinstance(response, dict):
            print_table([response])
        else:
            print_json(response)


@news_app.command("create")
def create_news(
    title: str = typer.Option(..., "-t", "--title", help="News title"),
    message: str = typer.Option(..., "-m", "--message", help="News message"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Create a new news item."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    data: dict[str, Any] = {
        "title": title,
        "message": message,
    }

    response = client.post_sync("/news/add", data={"News": data})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        news_id = response.get("News", {}).get("id", "Unknown")
        typer.echo(f"News item created successfully: {news_id}")


@news_app.command("edit")
def edit_news(
    news_id: int = typer.Argument(..., help="News ID to edit"),
    title: str | None = typer.Option(None, "-t", "--title", help="New title"),
    message: str | None = typer.Option(None, "-m", "--message", help="New message"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Edit a news item."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    data: dict[str, Any] = {}
    if title:
        data["title"] = title
    if message:
        data["message"] = message

    if not data:
        typer.echo("No changes specified", err=True)
        raise typer.Exit(1)

    response = client.post_sync(f"/news/edit/{news_id}", data={"News": data})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"News item {news_id} updated successfully")


@news_app.command("delete")
def delete_news(
    news_id: int = typer.Argument(..., help="News ID to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Force deletion without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Delete a news item."""
    from misp_cli.cli.app import get_app

    if not force:
        typer.confirm(f"Are you sure you want to delete news item {news_id}?", abort=True)

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/news/delete/{news_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"News item {news_id} deleted successfully")


@news_app.command("publish")
def publish_news(
    news_id: int = typer.Argument(..., help="News ID to publish"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Publish a news item."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/news/publish/{news_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"News item {news_id} published successfully")


@news_app.command("unpublish")
def unpublish_news(
    news_id: int = typer.Argument(..., help="News ID to unpublish"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Unpublish a news item."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/news/unpublish/{news_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"News item {news_id} unpublished")
