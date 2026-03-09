"""Sharing group management commands for MISP CLI."""

from typing import Any

import typer

from misp_cli.cli.output import get_output_format, print_csv, print_json, print_table

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
    # Show help if requested or no subcommand given
    if help or ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


@sharing_groups_app.command("list")
def list_sharing_groups(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of sharing groups"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """List all sharing groups."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    params: dict[str, Any] = {
        "limit": limit,
        "page": page,
    }

    response = client.get_sync("/sharing_groups/index", params=params)

    output_format = get_output_format(config, json_output, table_output, csv_output)
    sharing_groups = response.get("sharing_groups", response.get("data", []))

    if output_format == "csv":
        print_csv(sharing_groups)
    elif output_format == "table":
        print_table(sharing_groups)
    else:
        print_json(sharing_groups)


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
        print_json(response)
    else:
        if isinstance(response, dict):
            print_table([response])
        else:
            print_json(response)


@sharing_groups_app.command("create")
def create_sharing_group(
    name: str = typer.Option(..., "-n", "--name", help="Sharing group name"),
    description: str | None = typer.Option(None, "-d", "--description", help="Description"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Create a new sharing group."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    data: dict[str, Any] = {
        "name": name,
    }
    if description:
        data["description"] = description

    response = client.post_sync("/sharing_groups/add", data={"SharingGroup": data})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        sg_id = response.get("SharingGroup", {}).get("id", "Unknown")
        typer.echo(f"Sharing group created successfully: {sg_id}")


@sharing_groups_app.command("edit")
def edit_sharing_group(
    sharing_group_id: int = typer.Argument(..., help="Sharing group ID to edit"),
    name: str | None = typer.Option(None, "-n", "--name", help="New name"),
    description: str | None = typer.Option(None, "-d", "--description", help="New description"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Edit a sharing group."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    data: dict[str, Any] = {}
    if name:
        data["name"] = name
    if description:
        data["description"] = description

    if not data:
        typer.echo("No changes specified", err=True)
        raise typer.Exit(1)

    response = client.post_sync(
        f"/sharing_groups/edit/{sharing_group_id}", data={"SharingGroup": data}
    )

    if config.output_format == "json" or json_output:
        print_json(response)
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
        typer.confirm(
            f"Are you sure you want to delete sharing group {sharing_group_id}?", abort=True
        )

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/sharing_groups/delete/{sharing_group_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
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
        f"/sharing_groups/addOrg/{sharing_group_id}", data={"Organisation": {"id": org_id}}
    )

    if config.output_format == "json" or json_output:
        print_json(response)
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
        f"/sharing_groups/removeOrg/{sharing_group_id}", data={"Organisation": {"id": org_id}}
    )

    if config.output_format == "json" or json_output:
        print_json(response)
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
        f"/sharing_groups/addServer/{sharing_group_id}", data={"Server": {"id": server_id}}
    )

    if config.output_format == "json" or json_output:
        print_json(response)
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
        f"/sharing_groups/removeServer/{sharing_group_id}", data={"Server": {"id": server_id}}
    )

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo("Server removed successfully")
