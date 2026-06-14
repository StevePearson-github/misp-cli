"""Decaying model management commands for MISP CLI."""

from typing import Any

import typer

from misp_cli.cli.output import (
    COUNT_OPTION,
    get_output_format,
    print_count,
    print_csv,
    print_json,
    print_table,
)

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
    # Show help if requested or no subcommand given
    if help or ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


@decaying_models_app.command("list")
def list_decaying_models(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of models"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
    count: bool = COUNT_OPTION,
):
    """List all decaying models."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    effective_limit = 0 if count is True else limit
    params: dict[str, Any] = {"page": page}
    if effective_limit:
        params["limit"] = effective_limit

    response = client.get_sync("/decayingModel/index.json", params=params)

    output_format = get_output_format(config, json_output, table_output, csv_output)
    models = response.get("DecayingModel", response.get("data", []))

    if count is True:
        print_count(models, json_output, output_format)

    if output_format == "csv":
        print_csv(models)
    elif output_format == "table":
        print_table(models)
    else:
        print_json(models)


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
        print_json(response)
    else:
        if isinstance(response, dict):
            print_table([response])
        else:
            print_json(response)


@decaying_models_app.command("enable")
def enable_decaying_model(
    model_id: int = typer.Argument(..., help="Model ID to enable"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Enable a decaying model."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/decayingModels/enable/{model_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Decaying model {model_id} enabled")


@decaying_models_app.command("disable")
def disable_decaying_model(
    model_id: int = typer.Argument(..., help="Model ID to disable"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Disable a decaying model."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/decayingModels/disable/{model_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Decaying model {model_id} disabled")


@decaying_models_app.command("import")
def import_decaying_model(
    model_file: str = typer.Argument(..., help="Path to model file (JSON)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Import a decaying model from a JSON file."""
    import json as json_module

    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    try:
        with open(model_file) as f:
            model_data = json_module.load(f)
    except FileNotFoundError:
        typer.echo(f"Error: File {model_file} not found", err=True)
        raise typer.Exit(1) from None
    except json_module.JSONDecodeError:
        typer.echo(f"Error: Invalid JSON in {model_file}", err=True)
        raise typer.Exit(1) from None

    response = client.post_sync("/decayingModels/import", data={"DecayingModel": model_data})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        model_id = response.get("DecayingModel", {}).get("id", "Unknown")
        typer.echo(f"Decaying model imported successfully: {model_id}")


@decaying_models_app.command("export")
def export_decaying_model(
    model_id: int = typer.Argument(..., help="Model ID to export"),
    output_file: str | None = typer.Option(None, "-o", "--output", help="Output file path"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Export a decaying model to a JSON file."""
    import json as json_module

    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/decayingModels/export/{model_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    elif output_file:
        with open(output_file, "w") as f:
            json_module.dump(response, f, indent=2)
        typer.echo(f"Exported to {output_file}")
    else:
        print_json(response)


@decaying_models_app.command("delete")
def delete_decaying_model(
    model_id: int = typer.Argument(..., help="Model ID to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Force deletion without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Delete a decaying model."""
    from misp_cli.cli.app import get_app

    if not force:
        typer.confirm(f"Are you sure you want to delete decaying model {model_id}?", abort=True)

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/decayingModels/delete/{model_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Decaying model {model_id} deleted successfully")
