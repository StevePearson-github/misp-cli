"""Attribute blocklist management commands for MISP CLI."""

from typing import Any

import typer

from misp_cli.cli.output import get_output_format, print_csv, print_json, print_table

attribute_blocklists_app = typer.Typer(
    name="attribute-blocklists",
    help="Manage MISP attribute blocklists",
    add_help_option=True,
    invoke_without_command=True,
)


@attribute_blocklists_app.callback()
def attribute_blocklists_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP attribute blocklists."""
    if help:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@attribute_blocklists_app.command("list")
def list_attribute_blocklists(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of entries"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """List all attribute blocklist entries."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    params: dict[str, Any] = {
        "limit": limit,
        "page": page,
    }

    response = client.get_sync("/attributeBlocklists/index", params=params)

    output_format = get_output_format(config, json_output, table_output, csv_output)
    blocklists = response.get("attributeBlocklists", response.get("data", []))

    if output_format == "csv":
        print_csv(blocklists)
    elif output_format == "table":
        print_table(blocklists)
    else:
        print_json(blocklists)


@attribute_blocklists_app.command("add")
def add_attribute_blocklist(
    value: str = typer.Argument(..., help="Value to block"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Add an attribute value to the blocklist."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    data: dict[str, Any] = {
        "value": value,
    }

    response = client.post_sync("/attributeBlocklists/add", data={"AttributeBlocklist": data})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        blocklist_id = response.get("AttributeBlocklist", {}).get("id", "Unknown")
        typer.echo(f"Attribute blocklist entry created: {blocklist_id}")


@attribute_blocklists_app.command("remove")
def remove_attribute_blocklist(
    blocklist_id: int = typer.Argument(..., help="Blocklist entry ID to remove"),
    force: bool = typer.Option(False, "-f", "--force", help="Force without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Remove an attribute from the blocklist."""
    from misp_cli.cli.app import get_app

    if not force:
        typer.confirm(
            f"Are you sure you want to remove blocklist entry {blocklist_id}?", abort=True
        )

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/attributeBlocklists/delete/{blocklist_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Blocklist entry {blocklist_id} removed successfully")


@attribute_blocklists_app.command("bulk-add")
def bulk_add_attribute_blocklist(
    file_path: str = typer.Argument(..., help="Path to file with values (one per line)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Bulk add values to the attribute blocklist from a file."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    try:
        with open(file_path) as f:
            values = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        typer.echo(f"Error: File {file_path} not found", err=True)
        raise typer.Exit(1)

    data: dict[str, Any] = {
        "values": "\n".join(values),
    }

    response = client.post_sync("/attributeBlocklists/bulkAdd", data={"AttributeBlocklist": data})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        added = response.get("added", 0)
        typer.echo(f"Added {added} values to blocklist")
