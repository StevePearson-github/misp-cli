"""Noticelist management commands for MISP CLI."""

import json
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table

from misp_cli.core.config import MISPProfile

noticelists_app = typer.Typer(
    name="noticelists",
    help="Manage MISP notice lists",
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


@noticelists_app.command("list")
def list_noticelists(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of noticelists"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List all noticelists."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    params: Dict[str, Any] = {
        "limit": limit,
        "page": page,
    }
    
    response = client.get_sync("/noticelists/index", params=params)
    
    output_format = _get_output_format(config, json_output, table_output)
    noticelists = response.get("noticelists", response.get("data", []))
    
    if output_format == "table":
        _print_table(noticelists)
    else:
        _print_json(noticelists)


@noticelists_app.command("show")
def show_noticelist(
    noticelist_id: int = typer.Argument(..., help="Noticelist ID to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific noticelist."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/noticelists/view/{noticelist_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            _print_json(response)


@noticelists_app.command("enabled")
def list_enabled(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List enabled noticelists."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync("/noticelists/enabled")
    
    output_format = _get_output_format(config, json_output, table_output)
    noticelists = response.get("noticelists", response.get("data", []))
    
    if output_format == "table":
        _print_table(noticelists)
    else:
        _print_json(noticelists)


@noticelists_app.command("toggle")
def toggle_noticelist(
    noticelist_id: int = typer.Argument(..., help="Noticelist ID to toggle"),
    enable: bool = typer.Option(False, "--enable", help="Enable the noticelist"),
    disable: bool = typer.Option(False, "--disable", help="Disable the noticelist"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Enable or disable a noticelist."""
    from misp_cli.cli.app import get_app
    
    if not enable and not disable:
        typer.echo("Either --enable or --disable must be specified", err=True)
        raise typer.Exit(1)
    
    app = get_app()
    config = app.profile
    client = app.client
    
    action = "enable" if enable else "disable"
    response = client.post_sync(f"/noticelists/{action}/{noticelist_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Noticelist {noticelist_id} {action}d successfully")


@noticelists_app.command("view")
def view_noticelist_entries(
    noticelist_id: int = typer.Argument(..., help="Noticelist ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """View entries of a noticelist."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/noticelists/view/{noticelist_id}", params={"entries": 1})
    
    output_format = _get_output_format(config, json_output, table_output)
    noticelist = response.get("Noticelist", response)
    entries = noticelist.get("NoticelistEntry", [])
    
    if output_format == "table":
        _print_table(entries)
    else:
        _print_json(entries)
