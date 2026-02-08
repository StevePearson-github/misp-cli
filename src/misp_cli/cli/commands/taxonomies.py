"""Taxonomy management commands for MISP CLI."""

import json
from typing import Any, Dict, List, Optional

import typer
from rich.table import Table

from misp_cli.core.config import MISPProfile

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


@taxonomies_app.command("list")
def list_taxonomies(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of taxonomies"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List all taxonomies."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    params: Dict[str, Any] = {
        "limit": limit,
        "page": page,
    }
    
    response = client.get_sync("/taxonomies/index", params=params)
    
    output_format = _get_output_format(config, json_output, table_output)
    taxonomies = response.get("taxonomies", response.get("data", []))
    
    if output_format == "table":
        _print_table(taxonomies)
    else:
        _print_json(taxonomies)


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
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            _print_json(response)


@taxonomies_app.command("enabled")
def list_enabled(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List enabled taxonomies."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync("/taxonomies/enabled")
    
    output_format = _get_output_format(config, json_output, table_output)
    taxonomies = response.get("taxonomies", response.get("data", []))
    
    if output_format == "table":
        _print_table(taxonomies)
    else:
        _print_json(taxonomies)


@taxonomies_app.command("toggle")
def toggle_taxonomy(
    taxonomy_id: int = typer.Argument(..., help="Taxonomy ID to toggle"),
    enable: bool = typer.Option(False, "--enable", help="Enable the taxonomy"),
    disable: bool = typer.Option(False, "--disable", help="Disable the taxonomy"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Enable or disable a taxonomy."""
    from misp_cli.cli.app import get_app
    
    if not enable and not disable:
        typer.echo("Either --enable or --disable must be specified", err=True)
        raise typer.Exit(1)
    
    app = get_app()
    config = app.profile
    client = app.client
    
    action = "enable" if enable else "disable"
    response = client.post_sync(f"/taxonomies/{action}/{taxonomy_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Taxonomy {taxonomy_id} {action}d successfully")


@taxonomies_app.command("machinetags")
def list_machinetags(
    taxonomy_id: int = typer.Argument(..., help="Taxonomy ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List machine tags for a taxonomy."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/taxonomies/view/{taxonomy_id}", params={"machinetags": 1})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        taxonomy = response.get("Taxonomy", response)
        machinetags = taxonomy.get("TaxonomyPredicate", [])
        _print_table(machinetags)


@taxonomies_app.command("index")
def taxonomy_index(
    taxonomy_namespace: str = typer.Argument(..., help="Taxonomy namespace"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Get taxonomy index for a namespace."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync("/taxonomies/index", params={"namespace": taxonomy_namespace})
    
    output_format = _get_output_format(config, json_output, table_output)
    taxonomies = response.get("taxonomies", response.get("data", []))
    
    if output_format == "table":
        _print_table(taxonomies)
    else:
        _print_json(taxonomies)


@taxonomies_app.command("preview")
def preview_taxonomy(
    taxonomy_id: int = typer.Argument(..., help="Taxonomy ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Preview taxonomy tags."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/taxonomies/preview/{taxonomy_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        _print_json(response)


@taxonomies_app.command("export")
def export_taxonomy(
    taxonomy_id: int = typer.Argument(..., help="Taxonomy ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Export a taxonomy."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/taxonomies/export/{taxonomy_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        _print_json(response)
