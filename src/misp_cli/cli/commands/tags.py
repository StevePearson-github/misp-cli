"""Tag management commands for MISP CLI."""

import json
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table

from misp_cli.core.config import MISPProfile

tags_app = typer.Typer(
    name="tags",
    help="Manage MISP tags",
)


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
    
    console = Console()
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


@tags_app.command("list")
def list_tags(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of tags"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List all tags."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    params: Dict[str, Any] = {
        "limit": limit,
        "page": page,
    }
    
    response = client.get_sync("/tags/index", params=params)
    
    output_format = _get_output_format(config, json_output, table_output)
    tags = response.get("Tag", response.get("tags", response.get("data", [])))
    
    if output_format == "table":
        _print_table(tags)
    else:
        _print_json(tags)


@tags_app.command("show")
def show_tag(
    tag_id: int = typer.Argument(..., help="Tag ID to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific tag."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/tags/view/{tag_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            _print_json(response)


@tags_app.command("search")
def search_tags(
    name: str = typer.Argument(..., help="Tag name to search for"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Search for tags by name."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync("/tags/index", params={"search": name})
    
    output_format = _get_output_format(config, json_output, table_output)
    tags = response.get("Tag", response.get("tags", response.get("data", [])))
    
    if output_format == "table":
        _print_table(tags)
    else:
        _print_json(tags)


@tags_app.command("create")
def create_tag(
    name: str = typer.Option(..., "-n", "--name", help="Tag name"),
    color: str = typer.Option("#0088cc", "-c", "--color", help="Tag color (hex)"),
    exportable: bool = typer.Option(False, "-e", "--exportable", help="Exportable tag"),
    hide_tag: bool = typer.Option(False, "--hide", help="Hide tag from export"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Create a new tag."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    data: Dict[str, Any] = {
        "name": name,
        "color": color,
        "exportable": exportable,
    }
    if hide_tag:
        data["hide_tag"] = hide_tag
    
    response = client.post_sync("/tags/add", data={"Tag": data})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        tag_id = response.get("Tag", {}).get("id", "Unknown")
        typer.echo(f"Tag created successfully: {tag_id}")


@tags_app.command("edit")
def edit_tag(
    tag_id: int = typer.Argument(..., help="Tag ID to edit"),
    name: Optional[str] = typer.Option(None, "-n", "--name", help="New tag name"),
    color: Optional[str] = typer.Option(None, "-c", "--color", help="New tag color"),
    exportable: Optional[bool] = typer.Option(None, "-e", "--exportable", help="Exportable tag"),
    hide_tag: Optional[bool] = typer.Option(None, "--hide", help="Hide tag from export"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Edit a tag."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    data: Dict[str, Any] = {}
    if name:
        data["name"] = name
    if color:
        data["color"] = color
    if exportable is not None:
        data["exportable"] = exportable
    if hide_tag is not None:
        data["hide_tag"] = hide_tag
    
    if not data:
        typer.echo("No changes specified", err=True)
        raise typer.Exit(1)
    
    response = client.post_sync(f"/tags/edit/{tag_id}", data={"Tag": data})
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Tag {tag_id} updated successfully")


@tags_app.command("delete")
def delete_tag(
    tag_id: int = typer.Argument(..., help="Tag ID to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Force deletion without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Delete a tag."""
    from misp_cli.cli.app import get_app
    
    if not force:
        typer.confirm(f"Are you sure you want to delete tag {tag_id}?", abort=True)
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.post_sync(f"/tags/delete/{tag_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo(f"Tag {tag_id} deleted successfully")


@tags_app.command("attach")
def attach_tag(
    event_id: int = typer.Argument(..., help="Event ID"),
    tag_id: int = typer.Option(..., "-t", "--tag-id", help="Tag ID to attach"),
    attribute_id: Optional[int] = typer.Option(None, "-a", "--attribute-id", help="Attribute ID (optional)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Attach a tag to an event or attribute."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    if attribute_id:
        response = client.post_sync(
            f"/attributes/addTag/{attribute_id}",
            data={"Tag": {"id": tag_id}}
        )
    else:
        response = client.post_sync(
            f"/events/addTag/{event_id}",
            data={"Tag": {"id": tag_id}}
        )
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo("Tag attached successfully")


@tags_app.command("detach")
def detach_tag(
    event_id: int = typer.Argument(..., help="Event ID"),
    tag_id: int = typer.Option(..., "-t", "--tag-id", help="Tag ID to detach"),
    attribute_id: Optional[int] = typer.Option(None, "-a", "--attribute-id", help="Attribute ID (optional)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Detach a tag from an event or attribute."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    if attribute_id:
        response = client.post_sync(
            f"/attributes/removeTag/{attribute_id}",
            data={"Tag": {"id": tag_id}}
        )
    else:
        response = client.post_sync(
            f"/events/removeTag/{event_id}",
            data={"Tag": {"id": tag_id}}
        )
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo("Tag detached successfully")


@tags_app.command("event-tags")
def list_event_tags(
    event_id: int = typer.Argument(..., help="Event ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List all tags for an event."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/events/view/{event_id}", params={"tags": 1})
    
    output_format = _get_output_format(config, json_output, table_output)
    event = response.get("Event", response)
    tags = event.get("Tag", [])
    
    if output_format == "table":
        _print_table(tags)
    else:
        _print_json(tags)
