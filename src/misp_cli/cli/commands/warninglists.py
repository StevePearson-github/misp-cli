"""Warninglist management commands for MISP CLI."""

import typer

from misp_cli.cli.output import (
    COUNT_OPTION,
    get_output_format,
    print_count,
    print_csv,
    print_json,
    print_table,
)

warninglists_app = typer.Typer(
    name="warninglists",
    help="Manage MISP warninglists",
    add_help_option=True,
    invoke_without_command=True,
)


@warninglists_app.callback()
def warninglists_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP warninglists."""
    # Show help if requested or no subcommand given
    if help or ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


@warninglists_app.command("list")
def list_warninglists(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
    count: bool = COUNT_OPTION,
):
    """List all warninglists."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync("/warninglists/index")

    output_format = get_output_format(config, json_output, table_output, csv_output)
    warninglists = response.get("warninglists", response.get("data", []))

    if count is True:
        print_count(warninglists, json_output, output_format)

    if output_format == "csv":
        print_csv(warninglists)
    elif output_format == "table":
        print_table(warninglists)
    else:
        print_json(warninglists)


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
        print_json(response)
    else:
        if isinstance(response, dict):
            print_table([response])
        else:
            print_json(response)


@warninglists_app.command("enable")
def enable_warninglist(
    warninglist_id: int = typer.Argument(..., help="Warninglist ID to enable"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Enable a warninglist."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/warninglists/enable/{warninglist_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Warninglist {warninglist_id} enabled")


@warninglists_app.command("disable")
def disable_warninglist(
    warninglist_id: int = typer.Argument(..., help="Warninglist ID to disable"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Disable a warninglist."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/warninglists/disable/{warninglist_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Warninglist {warninglist_id} disabled")


@warninglists_app.command("toggle")
def toggle_warninglist(
    warninglist_id: int = typer.Argument(..., help="Warninglist ID to toggle"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Toggle a warninglist on/off."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/warninglists/toggle/{warninglist_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Warninglist {warninglist_id} toggled")


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
        print_json(response)
    else:
        matches = response.get("matches", [])
        if matches:
            typer.echo(f"Value '{value}' matches {len(matches)} warninglist(s):")
            for match in matches:
                typer.echo(f"  - {match.get('name', 'Unknown')}")
        else:
            typer.echo(f"Value '{value}' does not match any warninglist")


@warninglists_app.command("import")
def import_warninglist(
    file_path: str = typer.Argument(..., help="Path to warninglist JSON file"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Import a warninglist from a JSON file."""
    import json

    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    try:
        with open(file_path) as f:
            warninglist_data = json.load(f)
    except FileNotFoundError:
        typer.echo(f"Error: File {file_path} not found", err=True)
        raise typer.Exit(1) from None
    except json.JSONDecodeError:
        typer.echo(f"Error: Invalid JSON in {file_path}", err=True)
        raise typer.Exit(1) from None

    response = client.post_sync("/warninglists/import", data={"Warninglist": warninglist_data})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        wl_id = response.get("Warninglist", {}).get("id", "Unknown")
        typer.echo(f"Warninglist imported successfully: {wl_id}")


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
        print_json(response)
    else:
        typer.echo(f"Warninglist {warninglist_id} deleted successfully")
