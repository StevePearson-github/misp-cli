"""Server management commands for MISP CLI."""

import json
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table

from misp_cli.core.config import MISPProfile

servers_app = typer.Typer(
    name="servers",
    help="Manage MISP servers",
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


@servers_app.command("list")
def list_servers(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of servers"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List all connected servers."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    params: Dict[str, Any] = {
        "limit": limit,
        "page": page,
    }
    
    response = client.get_sync("/servers/index", params=params)
    
    output_format = _get_output_format(config, json_output, table_output)
    servers = response.get("servers", response.get("data", []))
    
    if output_format == "table":
        _print_table(servers)
    else:
        _print_json(servers)


@servers_app.command("show")
def show_server(
    server_id: int = typer.Argument(..., help="Server ID to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific server."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/servers/view/{server_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            _print_json(response)


@servers_app.command("create")
def create_server(
    name: str = typer.Option(..., "-n", "--name", help="Server name"),
    url: str = typer.Option(..., "-u", "--url", help="Server URL"),
    organization_id: int = typer.Option(..., "-o", "--org-id", help="Organization ID"),
    auth_key: str = typer.Option(..., "-k", "--auth-key", help="Authentication key"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Add a new server connection."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    data: Dict[str, Any] = {
        "name": name,
        "url": url,
        "organisation_id": organization_id,
        "authkey": auth_key,
    }
    
    response = client.post_sync("/servers/add", data={"Server": data})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        server_id = response.get("Server", {}).get("id", "Unknown")
        typer.echo(f"Server created successfully: {server_id}")


@servers_app.command("edit")
def edit_server(
    server_id: int = typer.Argument(..., help="Server ID to edit"),
    name: Optional[str] = typer.Option(None, "-n", "--name", help="New name"),
    url: Optional[str] = typer.Option(None, "-u", "--url", help="New URL"),
    auth_key: Optional[str] = typer.Option(None, "-k", "--auth-key", help="New auth key"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Edit a server connection."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    data: Dict[str, Any] = {}
    if name:
        data["name"] = name
    if url:
        data["url"] = url
    if auth_key:
        data["authkey"] = auth_key
    
    if not data:
        typer.echo("No changes specified", err=True)
        raise typer.Exit(1)
    
    response = client.post_sync(f"/servers/edit/{server_id}", data={"Server": data})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Server {server_id} updated successfully")


@servers_app.command("delete")
def delete_server(
    server_id: int = typer.Argument(..., help="Server ID to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Force deletion without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Delete a server connection."""
    from misp_cli.cli.app import get_app
    
    if not force:
        typer.confirm(f"Are you sure you want to delete server {server_id}?", abort=True)
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(f"/servers/delete/{server_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Server {server_id} deleted successfully")


@servers_app.command("pull")
def pull_from_server(
    server_id: int = typer.Argument(..., help="Server ID to pull from"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Pull events from a server."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(f"/servers/pull/{server_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Pulled events from server {server_id} successfully")


@servers_app.command("push")
def push_to_server(
    server_id: int = typer.Argument(..., help="Server ID to push to"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Push events to a server."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(f"/servers/push/{server_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Pushed events to server {server_id} successfully")


@servers_app.command("test")
def test_server(
    server_id: int = typer.Argument(..., help="Server ID to test"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Test connection to a server."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/servers/test/{server_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        result = response.get("Server", {})
        status = result.get("status", "unknown")
        if status == "OK":
            typer.echo(f"Server {server_id} test: SUCCESS")
        else:
            typer.echo(f"Server {server_id} test: {status}")


@servers_app.command("sync")
def sync_server(
    server_id: int = typer.Argument(..., help="Server ID to sync with"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Sync with a server."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(f"/servers/sync/{server_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Synced with server {server_id} successfully")


@servers_app.command("status")
def server_status(
    server_id: int = typer.Argument(..., help="Server ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Get server status."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/servers/status/{server_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        _print_json(response)
