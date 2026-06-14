"""Object template management commands for MISP CLI."""

import typer

from misp_cli.cli.output import (
    COUNT_OPTION,
    get_output_format,
    print_count,
    print_csv,
    print_json,
    print_table,
)

object_templates_app = typer.Typer(
    name="object-templates",
    help="Manage MISP object templates",
    add_help_option=True,
    invoke_without_command=True,
)


@object_templates_app.callback()
def object_templates_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP object templates."""
    # Show help if requested or no subcommand given
    if help or ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


@object_templates_app.command("list")
def list_object_templates(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
    count: bool = COUNT_OPTION,
):
    """List all object templates."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync("/objectTemplates/index")

    output_format = get_output_format(config, json_output, table_output, csv_output)
    templates = response.get("objectTemplates", response.get("data", []))

    if count is True:
        print_count(templates, json_output, output_format)

    if output_format == "csv":
        print_csv(templates)
    elif output_format == "table":
        print_table(templates)
    else:
        print_json(templates)


@object_templates_app.command("show")
def show_object_template(
    template_id: int = typer.Argument(..., help="Template ID to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific object template."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/objectTemplates/view/{template_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        if isinstance(response, dict):
            print_table([response])
        else:
            print_json(response)


@object_templates_app.command("delete")
def delete_object_template(
    template_id: int = typer.Argument(..., help="Template ID to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Force deletion without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Delete an object template."""
    from misp_cli.cli.app import get_app

    if not force:
        typer.confirm(f"Are you sure you want to delete template {template_id}?", abort=True)

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/objectTemplates/delete/{template_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Template {template_id} deleted successfully")


@object_templates_app.command("import")
def import_object_template(
    file_path: str = typer.Argument(..., help="Path to template JSON file"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Import an object template from a JSON file."""
    import json

    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    try:
        with open(file_path) as f:
            template_data = json.load(f)
    except FileNotFoundError:
        typer.echo(f"Error: File {file_path} not found", err=True)
        raise typer.Exit(1) from None
    except json.JSONDecodeError:
        typer.echo(f"Error: Invalid JSON in {file_path}", err=True)
        raise typer.Exit(1) from None

    response = client.post_sync("/objectTemplates/import", data={"ObjectTemplate": template_data})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        template_id = response.get("ObjectTemplate", {}).get("id", "Unknown")
        typer.echo(f"Template imported successfully: {template_id}")


@object_templates_app.command("export")
def export_object_template(
    template_id: int = typer.Argument(..., help="Template ID to export"),
    output_file: str | None = typer.Option(None, "-o", "--output", help="Output file path"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Export an object template to a JSON file."""
    import json

    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/objectTemplates/export/{template_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    elif output_file:
        with open(output_file, "w") as f:
            json.dump(response, f, indent=2)
        typer.echo(f"Exported to {output_file}")
    else:
        print_json(response)
