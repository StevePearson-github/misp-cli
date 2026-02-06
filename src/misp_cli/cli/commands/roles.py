"""Role management commands for MISP CLI."""

import json
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table

from misp_cli.core.config import MISPProfile

roles_app = typer.Typer(
    name="roles",
    help="Manage MISP roles",
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


@roles_app.command("list")
def list_roles(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List all roles."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync("/roles/index")
    
    output_format = _get_output_format(config, json_output, table_output)
    roles = response.get("roles", response.get("data", []))
    
    if output_format == "table":
        _print_table(roles)
    else:
        _print_json(roles)


@roles_app.command("show")
def show_role(
    role_id: int = typer.Argument(..., help="Role ID to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific role."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/roles/view/{role_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            _print_json(response)


@roles_app.command("permissions")
def show_permissions(
    role_id: int = typer.Argument(..., help="Role ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show permissions for a role."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/roles/view/{role_id}", params={"permissions": 1})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        role = response.get("Role", response)
        permissions = role.get("Permission", [])
        _print_table(permissions)
