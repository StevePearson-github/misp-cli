"""Decaying model management commands for MISP CLI."""

import json
from typing import Any, Dict, List, Optional

import typer
from rich.table import Table

from misp_cli.core.config import MISPProfile

decaying_models_app = typer.Typer(
    name="decaying-models",
    help="Manage MISP decaying models",
    add_help_option=True,
    invoke_without_command=True,
)


@decaying_models_app.callback()
def decaying_models_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP decaying models."""
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


@decaying_models_app.command("list")
def list_decaying_models(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of models"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List all decaying models."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    params: Dict[str, Any] = {
        "limit": limit,
        "page": page,
    }
    
    response = client.get_sync("/decayingModels/index", params=params)
    
    output_format = _get_output_format(config, json_output, table_output)
    models = response.get("decayingModels", response.get("data", []))
    
    if output_format == "table":
        _print_table(models)
    else:
        _print_json(models)


@decaying_models_app.command("show")
def show_decaying_model(
    model_id: int = typer.Argument(..., help="Model ID to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific decaying model."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/decayingModels/view/{model_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            _print_json(response)


@decaying_models_app.command("toggle")
def toggle_decaying_model(
    model_id: int = typer.Argument(..., help="Model ID to toggle"),
    enable: bool = typer.Option(False, "--enable", help="Enable the model"),
    disable: bool = typer.Option(False, "--disable", help="Disable the model"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Enable or disable a decaying model."""
    from misp_cli.cli.app import get_app
    
    if not enable and not disable:
        typer.echo("Either --enable or --disable must be specified", err=True)
        raise typer.Exit(1)
    
    app = get_app()
    config = app.profile
    client = app.client
    
    action = "enable" if enable else "disable"
    response = client.post_sync(f"/decayingModels/{action}/{model_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Decaying model {model_id} {action}d successfully")


@decaying_models_app.command("compute")
def compute_score(
    model_id: int = typer.Argument(..., help="Model ID"),
    value: str = typer.Argument(..., help="Value to compute score for"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Compute score for a value using a decaying model."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(
        f"/decayingModels/computeScore/{model_id}",
        params={"value": value}
    )
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        result = response.get("DecayingModel", {})
        typer.echo(f"Score: {result.get('score', 'N/A')}")


@decaying_models_app.command("export")
def export_model(
    model_id: int = typer.Argument(..., help="Model ID to export"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Export a decaying model."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/decayingModels/export/{model_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        _print_json(response)
