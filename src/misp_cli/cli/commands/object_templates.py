"""Object template management commands for MISP CLI."""

import json
from typing import Any, Dict, List, Optional

import typer
from rich.table import Table

from misp_cli.core.config import MISPProfile

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


@object_templates_app.command("list")
def list_templates(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of templates"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List all object templates."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    params: Dict[str, Any] = {
        "limit": limit,
        "page": page,
    }
    
    response = client.get_sync("/objectTemplates/index", params=params)
    
    output_format = _get_output_format(config, json_output, table_output)
    templates = response.get("object_templates", response.get("data", []))
    
    if output_format == "table":
        _print_table(templates)
    else:
        _print_json(templates)


@object_templates_app.command("show")
def show_template(
    template_id: int = typer.Argument(..., help="Template ID to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific template."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/objectTemplates/view/{template_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            _print_json(response)


@object_templates_app.command("templates-elements")
def show_template_elements(
    template_id: int = typer.Argument(..., help="Template ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show elements of a template."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/objectTemplates/view/{template_id}", params={"elements": 1})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        template = response.get("ObjectTemplate", response)
        elements = template.get("ObjectTemplateElement", [])
        _print_table(elements)


@object_templates_app.command("add")
def add_template(
    path: str = typer.Argument(..., help="Path to template JSON file"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Add a new object template from a JSON file."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    with open(path, "r") as f:
        template_data = json.load(f)
    
    response = client.post_sync("/objectTemplates/add", data={"ObjectTemplate": template_data})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        template_id = response.get("ObjectTemplate", {}).get("id", "Unknown")
        typer.echo(f"Template added successfully: {template_id}")


@object_templates_app.command("delete")
def delete_template(
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
        _print_json(response)
    else:
        typer.echo(f"Template {template_id} deleted successfully")


@object_templates_app.command("describe")
def describe_template(
    template_name: str = typer.Argument(..., help="Template name"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Get template description by name."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync("/objectTemplates/describe", params={"name": template_name})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        _print_json(response)
