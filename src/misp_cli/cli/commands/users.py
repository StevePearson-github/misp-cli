"""User management commands for MISP CLI."""

import json
from typing import Any, Dict, List, Optional

import typer
from rich.table import Table

from misp_cli.core.config import MISPProfile

users_app = typer.Typer(
    name="users",
    help="Manage MISP users",
    add_help_option=True,
    invoke_without_command=True,
)


@users_app.callback()
def users_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP users."""
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


@users_app.command("list")
def list_users(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of users"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List all users."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    params: Dict[str, Any] = {
        "limit": limit,
        "page": page,
    }
    
    response = client.post_sync("/admin/users/index", data=params)
    
    output_format = _get_output_format(config, json_output, table_output)
    users = response if isinstance(response, list) else response.get("User", response.get("users", response.get("data", [])))
    
    if output_format == "table":
        _print_table(users)
    else:
        _print_json(users)


@users_app.command("show")
def show_user(
    user_id: int = typer.Argument(..., help="User ID to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific user."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/users/view/{user_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            _print_json(response)


@users_app.command("current")
def current_user(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show current user information."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync("/users/view/me")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            _print_json(response)


@users_app.command("create")
def create_user(
    email: str = typer.Option(..., "-e", "--email", help="User email"),
    org_id: int = typer.Option(..., "-o", "--org-id", help="Organisation ID"),
    role_id: int = typer.Option(..., "-r", "--role-id", help="Role ID"),
    first_name: str = typer.Option(..., "-f", "--first-name", help="First name"),
    last_name: str = typer.Option(..., "-l", "--last-name", help="Last name"),
    password: str = typer.Option(..., "-p", "--password", help="Password"),
    confirm_password: str = typer.Option(..., "-c", "--confirm-password", help="Confirm password"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Create a new user."""
    from misp_cli.cli.app import get_app
    
    if password != confirm_password:
        typer.echo("Passwords do not match", err=True)
        raise typer.Exit(1)
    
    app = get_app()
    config = app.profile
    client = app.client
    
    data: Dict[str, Any] = {
        "email": email,
        "org_id": org_id,
        "role_id": role_id,
        "first_name": first_name,
        "last_name": last_name,
        "password": password,
    }
    
    response = client.post_sync("/users/add", data={"User": data})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        user_id = response.get("User", {}).get("id", "Unknown")
        typer.echo(f"User created successfully: {user_id}")


@users_app.command("edit")
def edit_user(
    user_id: int = typer.Argument(..., help="User ID to edit"),
    email: Optional[str] = typer.Option(None, "-e", "--email", help="New email"),
    org_id: Optional[int] = typer.Option(None, "-o", "--org-id", help="New organisation ID"),
    role_id: Optional[int] = typer.Option(None, "-r", "--role-id", help="New role ID"),
    first_name: Optional[str] = typer.Option(None, "-f", "--first-name", help="New first name"),
    last_name: Optional[str] = typer.Option(None, "-l", "--last-name", help="New last name"),
    password: Optional[str] = typer.Option(None, "-p", "--password", help="New password"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Edit a user."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    data: Dict[str, Any] = {}
    if email:
        data["email"] = email
    if org_id:
        data["org_id"] = org_id
    if role_id:
        data["role_id"] = role_id
    if first_name:
        data["first_name"] = first_name
    if last_name:
        data["last_name"] = last_name
    if password:
        data["password"] = password
    
    if not data:
        typer.echo("No changes specified", err=True)
        raise typer.Exit(1)
    
    response = client.post_sync(f"/users/edit/{user_id}", data={"User": data})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"User {user_id} updated successfully")


@users_app.command("delete")
def delete_user(
    user_id: int = typer.Argument(..., help="User ID to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Force deletion without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Delete a user."""
    from misp_cli.cli.app import get_app
    
    if not force:
        typer.confirm(f"Are you sure you want to delete user {user_id}?", abort=True)
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(f"/users/delete/{user_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"User {user_id} deleted successfully")


@users_app.command("org-users")
def list_org_users(
    org_id: int = typer.Argument(..., help="Organisation ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List users in an organisation."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync("/admin/users/index", data={"org_id": org_id})
    
    output_format = _get_output_format(config, json_output, table_output)
    users = response if isinstance(response, list) else response.get("User", response.get("users", response.get("data", [])))
    
    if output_format == "table":
        _print_table(users)
    else:
        _print_json(users)


@users_app.command("admin")
def admin_user(
    user_id: int = typer.Argument(..., help="User ID"),
    enable: bool = typer.Option(False, "--enable", help="Enable admin"),
    disable: bool = typer.Option(False, "--disable", help="Disable admin"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Make a user an admin or remove admin status."""
    from misp_cli.cli.app import get_app
    
    if not enable and not disable:
        typer.echo("Either --enable or --disable must be specified", err=True)
        raise typer.Exit(1)
    
    app = get_app()
    config = app.profile
    client = app.client
    
    action = "admin" if enable else "removeadmin"
    response = client.post_sync(f"/users/{action}/{user_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        action_text = "made admin" if enable else "removed from admin"
        typer.echo(f"User {user_id} {action_text} successfully")


@users_app.command("disable")
def disable_user(
    user_id: int = typer.Argument(..., help="User ID to disable"),
    force: bool = typer.Option(False, "-f", "--force", help="Force without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Disable a user."""
    from misp_cli.cli.app import get_app
    
    if not force:
        typer.confirm(f"Are you sure you want to disable user {user_id}?", abort=True)
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(f"/users/disable/{user_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"User {user_id} disabled successfully")


@users_app.command("enable")
def enable_user(
    user_id: int = typer.Argument(..., help="User ID to enable"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Enable a user."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(f"/users/enable/{user_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"User {user_id} enabled successfully")


@users_app.command("field-changes")
def field_changes(
    user_id: int = typer.Argument(..., help="User ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show field changes for a user."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/users/fieldChanges/{user_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        _print_json(response)
