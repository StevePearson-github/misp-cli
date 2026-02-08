"""Role management commands for MISP CLI."""

import typer

from misp_cli.cli.output import get_output_format, print_csv, print_json, print_table

roles_app = typer.Typer(
    name="roles",
    help="Manage MISP roles",
    add_help_option=True,
    invoke_without_command=True,
)


@roles_app.callback()
def roles_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP roles."""
    if help:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@roles_app.command("list")
def list_roles(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """List all roles."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync("/roles/index")

    output_format = get_output_format(config, json_output, table_output, csv_output)
    roles = response.get("roles", response.get("data", []))

    if output_format == "csv":
        print_csv(roles)
    elif output_format == "table":
        print_table(roles)
    else:
        print_json(roles)


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
        print_json(response)
    else:
        if isinstance(response, dict):
            print_table([response])
        else:
            print_json(response)


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
        print_json(response)
    else:
        role = response.get("Role", response)
        permissions = role.get("Permission", [])
        print_table(permissions)
