"""News feed management commands for MISP CLI."""

import json
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table

from misp_cli.core.config import MISPProfile

news_app = typer.Typer(
    name="news",
    help="Manage MISP news feeds",
)


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
    
    console = Console()
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


@news_app.command("list")
def list_news(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of news items"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List all news items."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    params: Dict[str, Any] = {
        "limit": limit,
        "page": page,
    }
    
    response = client.get_sync("/news/index", params=params)
    
    output_format = _get_output_format(config, json_output, table_output)
    news_items = response.get("news", response.get("data", []))
    
    if output_format == "table":
        _print_table(news_items)
    else:
        _print_json(news_items)


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
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            _print_json(response)


@news_app.command("create")
def create_news(
    message: str = typer.Option(..., "-m", "--message", help="News message"),
    title: str = typer.Option(..., "-t", "--title", help="News title"),
    url: Optional[str] = typer.Option(None, "-u", "--url", help="Related URL"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Create a news item."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    data: Dict[str, Any] = {
        "message": message,
        "title": title,
    }
    if url:
        data["url"] = url
    
    response = client.post_sync("/news/add", data={"News": data})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        news_id = response.get("News", {}).get("id", "Unknown")
        typer.echo(f"News item created successfully: {news_id}")


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
        _print_json(response)
    else:
        typer.echo(f"News item {news_id} deleted successfully")


@news_app.command("edit")
def edit_news(
    news_id: int = typer.Argument(..., help="News ID to edit"),
    message: Optional[str] = typer.Option(None, "-m", "--message", help="New message"),
    title: Optional[str] = typer.Option(None, "-t", "--title", help="New title"),
    url: Optional[str] = typer.Option(None, "-u", "--url", help="New URL"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Edit a news item."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    data: Dict[str, Any] = {}
    if message:
        data["message"] = message
    if title:
        data["title"] = title
    if url is not None:
        data["url"] = url
    
    if not data:
        typer.echo("No changes specified", err=True)
        raise typer.Exit(1)
    
    response = client.post_sync(f"/news/edit/{news_id}", data={"News": data})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"News item {news_id} updated successfully")
