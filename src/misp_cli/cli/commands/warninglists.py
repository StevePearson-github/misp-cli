"""Warninglist management commands for MISP CLI."""

import json
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table

from misp_cli.core.config import MISPProfile

warninglists_app = typer.Typer(
    name="warninglists",
    help="Manage MISP warninglists",
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


@warninglists_app.command("list")
def list_warninglists(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of warninglists"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List all warninglists."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    params: Dict[str, Any] = {
        "limit": limit,
        "page": page,
    }
    
    response = client.get_sync("/warninglists/index", params=params)
    
    output_format = _get_output_format(config, json_output, table_output)
    warninglists = response.get("Warninglists", response.get("warninglists", response.get("data", [])))
    
    if output_format == "table":
        _print_table(warninglists)
    else:
        _print_json(warninglists)


@warninglists_app.command("show")
def show_warninglist(
    warninglist_id: int = typer.Argument(..., help="Warninglist ID to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific warninglist."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/warninglists/view/{warninglist_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            _print_json(response)


@warninglists_app.command("toggle")
def toggle_warninglist(
    warninglist_id: int = typer.Argument(..., help="Warninglist ID to toggle"),
    enable: bool = typer.Option(False, "--enable", help="Enable the warninglist"),
    disable: bool = typer.Option(False, "--disable", help="Disable the warninglist"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Enable or disable a warninglist."""
    from misp_cli.cli.app import get_app
    
    if not enable and not disable:
        typer.echo("Either --enable or --disable must be specified", err=True)
        raise typer.Exit(1)
    
    app = get_app()
    config = app.profile
    client = app.client
    
    action = "enable" if enable else "disable"
    response = client.post_sync(f"/warninglists/{action}/{warninglist_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Warninglist {warninglist_id} {action}d successfully")


@warninglists_app.command("enabled")
def list_enabled(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List enabled warninglists."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync("/warninglists/enabled")
    
    output_format = _get_output_format(config, json_output, table_output)
    warninglists = response.get("Warninglists", response.get("warninglists", response.get("data", [])))
    
    if output_format == "table":
        _print_table(warninglists)
    else:
        _print_json(warninglists)


@warninglists_app.command("check")
def check_warninglist(
    value: str = typer.Argument(..., help="Value to check against warninglists"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Check a value against enabled warninglists."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync("/warninglists/check", params={"value": value})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            _print_json(response)


@warninglists_app.command("checkMany")
def check_many_warninglists(
    values: str = typer.Argument(..., help="Comma-separated values to check"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Check multiple values against enabled warninglists."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    values_list = [v.strip() for v in values.split(",")]
    
    response = client.get_sync("/warninglists/checkMany", params={"values": values_list})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        _print_json(response)


@warninglists_app.command("events")
def events_warninglist(
    warninglist_id: int = typer.Argument(..., help="Warninglist ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Get events related to a warninglist."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/warninglists/events/{warninglist_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        _print_json(response)


@warninglists_app.command("delete")
def delete_warninglist(
    warninglist_id: int = typer.Argument(..., help="Warninglist ID to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Force deletion without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Delete a warninglist."""
    from misp_cli.cli.app import get_app
    
    if not force:
        typer.confirm(f"Are you sure you want to delete warninglist {warninglist_id}?", abort=True)
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(f"/warninglists/delete/{warninglist_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Warninglist {warninglist_id} deleted successfully")


@warninglists_app.command("toggle_all")
def toggle_all_warninglists(
    enable: bool = typer.Option(False, "--enable", help="Enable all warninglists"),
    disable: bool = typer.Option(False, "--disable", help="Disable all warninglists"),
    force: bool = typer.Option(False, "-f", "--force", help="Force without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Enable or disable all warninglists."""
    from misp_cli.cli.app import get_app
    
    if not enable and not disable:
        typer.echo("Either --enable or --disable must be specified", err=True)
        raise typer.Exit(1)
    
    if not force:
        action = "enable" if enable else "disable"
        typer.confirm(f"Are you sure you want to {action} all warninglists?", abort=True)
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync("/warninglists/toggleWarninglists")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo("Warninglists toggled successfully")
