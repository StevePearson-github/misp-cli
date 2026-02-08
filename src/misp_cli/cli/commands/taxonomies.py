"""Taxonomy management commands for MISP CLI."""

from typing import Any

import typer

from misp_cli.cli.output import get_output_format, print_csv, print_json, print_table

taxonomies_app = typer.Typer(
    name="taxonomies",
    help="Manage MISP taxonomies",
    add_help_option=True,
    invoke_without_command=True,
)


@taxonomies_app.callback()
def taxonomies_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP taxonomies."""
    if help:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@taxonomies_app.command("list")
def list_taxonomies(
    enabled: bool = typer.Option(False, "-e", "--enabled", help="Show only enabled taxonomies"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """List all taxonomies."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    params: dict[str, Any] = {}
    if enabled:
        params["enabled"] = "true"

    response = client.get_sync("/taxonomies/index", params=params)

    output_format = get_output_format(config, json_output, table_output, csv_output)
    taxonomies = response.get("taxonomies", response.get("data", []))

    if output_format == "csv":
        print_csv(taxonomies)
    elif output_format == "table":
        print_table(taxonomies)
    else:
        print_json(taxonomies)


@taxonomies_app.command("show")
def show_taxonomy(
    taxonomy_id: int = typer.Argument(..., help="Taxonomy ID to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific taxonomy."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/taxonomies/view/{taxonomy_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        if isinstance(response, dict):
            print_table([response])
        else:
            print_json(response)


@taxonomies_app.command("enable")
def enable_taxonomy(
    taxonomy_id: int = typer.Argument(..., help="Taxonomy ID to enable"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Enable a taxonomy."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/taxonomies/enable/{taxonomy_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Taxonomy {taxonomy_id} enabled")


@taxonomies_app.command("disable")
def disable_taxonomy(
    taxonomy_id: int = typer.Argument(..., help="Taxonomy ID to disable"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Disable a taxonomy."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/taxonomies/disable/{taxonomy_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Taxonomy {taxonomy_id} disabled")


@taxonomies_app.command("toggle")
def toggle_taxonomy(
    taxonomy_id: int = typer.Argument(..., help="Taxonomy ID to toggle"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Toggle a taxonomy on/off."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/taxonomies/toggle/{taxonomy_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Taxonomy {taxonomy_id} toggled")


@taxonomies_app.command("import")
def import_taxonomy(
    taxonomy_id: int = typer.Argument(..., help="Taxonomy ID to import"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Import a taxonomy by ID."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/taxonomies/import/{taxonomy_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Taxonomy {taxonomy_id} imported successfully")


@taxonomies_app.command("delete")
def delete_taxonomy(
    taxonomy_id: int = typer.Argument(..., help="Taxonomy ID to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Force deletion without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Delete a taxonomy."""
    from misp_cli.cli.app import get_app

    if not force:
        typer.confirm(f"Are you sure you want to delete taxonomy {taxonomy_id}?", abort=True)

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/taxonomies/delete/{taxonomy_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Taxonomy {taxonomy_id} deleted successfully")


@taxonomies_app.command("tags")
def list_taxonomy_tags(
    taxonomy_id: int = typer.Argument(..., help="Taxonomy ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """List all tags in a taxonomy."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/taxonomies/tags/{taxonomy_id}")

    output_format = get_output_format(config, json_output, False, csv_output)
    tags = response.get("tags", response.get("data", []))

    if output_format == "csv":
        print_csv(tags)
    else:
        print_json(tags)
