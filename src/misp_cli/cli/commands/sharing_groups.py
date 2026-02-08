"""Sharing group management commands for MISP CLI."""

import json
from typing import Any, Dict, List, Optional

import typer
from rich.table import Table

from misp_cli.core.config import MISPProfile

sharing_groups_app = typer.Typer(
    name="sharing-groups",
    help="Manage MISP sharing groups",
    add_help_option=True,
    invoke_without_command=True,
)


@sharing_groups_app.callback()
def sharing_groups_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP sharing groups."""
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


@sharing_groups_app.command("list")
def list_sharing_groups(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of sharing groups"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List all sharing groups."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    params: Dict[str, Any] = {
        "limit": limit,
        "page": page,
    }
    
    response = client.get_sync("/sharing_groups/index", params=params)
    
    output_format = _get_output_format(config, json_output, table_output)
    sharing_groups = response.get("sharing_groups", response.get("data", []))
    
    if output_format == "table":
        _print_table(sharing_groups)
    else:
        _print_json(sharing_groups)


@sharing_groups_app.command("show")
def show_sharing_group(
    sharing_group_id: int = typer.Argument(..., help="Sharing group ID to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific sharing group."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/sharing_groups/view/{sharing_group_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            _print_json(response)


@sharing_groups_app.command("create")
def create_sharing_group(
    name: str = typer.Option(..., "-n", "--name", help="Sharing group name"),
    description: Optional[str] = typer.Option(None, "-d", "--description", help="Description"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Create a new sharing group."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    data: Dict[str, Any] = {
        "name": name,
    }
    if description:
        data["description"] = description
    
    response = client.post_sync("/sharing_groups/add", data={"SharingGroup": data})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        sg_id = response.get("SharingGroup", {}).get("id", "Unknown")
        typer.echo(f"Sharing group created successfully: {sg_id}")


@sharing_groups_app.command("edit")
def edit_sharing_group(
    sharing_group_id: int = typer.Argument(..., help="Sharing group ID to edit"),
    name: Optional[str] = typer.Option(None, "-n", "--name", help="New name"),
    description: Optional[str] = typer.Option(None, "-d", "--description", help="New description"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Edit a sharing group."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    data: Dict[str, Any] = {}
    if name:
        data["name"] = name
    if description:
        data["description"] = description
    
    if not data:
        typer.echo("No changes specified", err=True)
        raise typer.Exit(1)
    
    response = client.post_sync(f"/sharing_groups/edit/{sharing_group_id}", data={"SharingGroup": data})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Sharing group {sharing_group_id} updated successfully")


@sharing_groups_app.command("delete")
def delete_sharing_group(
    sharing_group_id: int = typer.Argument(..., help="Sharing group ID to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Force deletion without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Delete a sharing group."""
    from misp_cli.cli.app import get_app
    
    if not force:
        typer.confirm(f"Are you sure you want to delete sharing group {sharing_group_id}?", abort=True)
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(f"/sharing_groups/delete/{sharing_group_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Sharing group {sharing_group_id} deleted successfully")


@sharing_groups_app.command("add-org")
def add_organization(
    sharing_group_id: int = typer.Argument(..., help="Sharing group ID"),
    org_id: int = typer.Option(..., "-o", "--org-id", help="Organization ID to add"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Add an organization to a sharing group."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(
        f"/sharing_groups/addOrg/{sharing_group_id}",
        data={"Organisation": {"id": org_id}}
    )
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo("Organization added successfully")


@sharing_groups_app.command("remove-org")
def remove_organization(
    sharing_group_id: int = typer.Argument(..., help="Sharing group ID"),
    org_id: int = typer.Option(..., "-o", "--org-id", help="Organization ID to remove"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Remove an organization from a sharing group."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(
        f"/sharing_groups/removeOrg/{sharing_group_id}",
        data={"Organisation": {"id": org_id}}
    )
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo("Organization removed successfully")


@sharing_groups_app.command("add-server")
def add_server(
    sharing_group_id: int = typer.Argument(..., help="Sharing group ID"),
    server_id: int = typer.Option(..., "-s", "--server-id", help="Server ID to add"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Add a server to a sharing group."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(
        f"/sharing_groups/addServer/{sharing_group_id}",
        data={"Server": {"id": server_id}}
    )
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo("Server added successfully")


@sharing_groups_app.command("remove-server")
def remove_server(
    sharing_group_id: int = typer.Argument(..., help="Sharing group ID"),
    server_id: int = typer.Option(..., "-s", "--server-id", help="Server ID to remove"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Remove a server from a sharing group."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(
        f"/sharing_groups/removeServer/{sharing_group_id}",
        data={"Server": {"id": server_id}}
    )
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo("Server removed successfully")
