"""Noticelist management commands for MISP CLI."""

import typer

from misp_cli.cli.output import (
    COUNT_OPTION,
    get_output_format,
    print_count,
    print_csv,
    print_json,
    print_table,
)

noticelists_app = typer.Typer(
    name="noticelists",
    help="Manage MISP noticelists",
    add_help_option=True,
    invoke_without_command=True,
)


@noticelists_app.callback()
def noticelists_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP noticelists."""
    # Show help if requested or no subcommand given
    if help or ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


@noticelists_app.command("list")
def list_noticelists(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
    count: bool = COUNT_OPTION,
):
    """List all noticelists."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync("/noticelists/index")

    output_format = get_output_format(config, json_output, table_output, csv_output)
    noticelists = response.get("noticelists", response.get("data", []))

    if count is True:
        print_count(noticelists, json_output)

    if output_format == "csv":
        print_csv(noticelists)
    elif output_format == "table":
        print_table(noticelists)
    else:
        print_json(noticelists)


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
        print_json(response)
    else:
        if isinstance(response, dict):
            print_table([response])
        else:
            print_json(response)


@noticelists_app.command("enable")
def enable_noticelist(
    noticelist_id: int = typer.Argument(..., help="Noticelist ID to enable"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Enable a noticelist."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/noticelists/enable/{noticelist_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Noticelist {noticelist_id} enabled")


@noticelists_app.command("disable")
def disable_noticelist(
    noticelist_id: int = typer.Argument(..., help="Noticelist ID to disable"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Disable a noticelist."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/noticelists/disable/{noticelist_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Noticelist {noticelist_id} disabled")


@noticelists_app.command("toggle")
def toggle_noticelist(
    noticelist_id: int = typer.Argument(..., help="Noticelist ID to toggle"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Toggle a noticelist on/off."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/noticelists/toggle/{noticelist_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Noticelist {noticelist_id} toggled")


@noticelists_app.command("import")
def import_noticelist(
    noticelist_id: int = typer.Argument(..., help="Noticelist ID to import"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Import a noticelist by ID."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/noticelists/import/{noticelist_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Noticelist {noticelist_id} imported successfully")


@noticelists_app.command("delete")
def delete_noticelist(
    noticelist_id: int = typer.Argument(..., help="Noticelist ID to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Force deletion without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Delete a noticelist."""
    from misp_cli.cli.app import get_app

    if not force:
        typer.confirm(f"Are you sure you want to delete noticelist {noticelist_id}?", abort=True)

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/noticelists/delete/{noticelist_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Noticelist {noticelist_id} deleted successfully")
