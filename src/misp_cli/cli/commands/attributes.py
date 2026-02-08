"""Attribute management commands for MISP CLI."""

from typing import Any

import typer
from rich.table import Table

from misp_cli.cli.output import get_output_format, print_csv, print_json

attributes_app = typer.Typer(
    name="attributes",
    help="Manage MISP attributes",
    add_help_option=True,
    invoke_without_command=True,
)


@attributes_app.callback()
def attributes_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP attributes."""
    if help:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def _print_table(data: list[dict], columns: list[str] | None = None) -> None:
    """Print data as a table with N/A for None values."""
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
            if value is None:
                row.append("N/A")
            elif isinstance(value, (dict, list)):
                row.append(str(len(value)))
            else:
                row.append(str(value))
        table.add_row(*row)

    console.print(table)


@attributes_app.command("list")
def list_attributes(
    event_id: int | None = typer.Option(None, "-e", "--event", help="Filter by event ID"),
    type: str | None = typer.Option(None, "-t", "--type", help="Filter by attribute type"),
    category: str | None = typer.Option(None, "-c", "--category", help="Filter by category"),
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of attributes"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    from_date: str | None = typer.Option(
        None, "--from", help="Start date filter (e.g., 2024-03-19, 2024-03-19T11:10:24Z, 7d)"
    ),
    to_date: str | None = typer.Option(
        None, "--to", help="End date filter (e.g., 2024-03-19, 2024-03-19T11:10:24Z, 14d)"
    ),
    last: str | None = typer.Option(
        None, "--last", help="Relative time filter (e.g., 5d, 12h, 30m, 1617875568)"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-T", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """List attributes with optional filtering."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    params: dict[str, Any] = {
        "limit": limit,
        "page": page,
    }
    if event_id:
        params["eventid"] = event_id
    if type:
        params["type"] = type
    if category:
        params["category"] = category
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    if last:
        params["last"] = last

    response = client.get_sync("/attributes/index", params=params)

    output_format = get_output_format(config, json_output, table_output, csv_output)

    # Unwrap nested Attribute structure: [{'Attribute': {...}}, ...] -> [{...}, ...]
    raw_attributes = response.get("attributes", response.get("data", []))
    if raw_attributes and isinstance(raw_attributes, list):
        # Check if each item is wrapped in "Attribute" key
        if all(isinstance(item, dict) and "Attribute" in item for item in raw_attributes):
            attributes = [item["Attribute"] for item in raw_attributes]
        else:
            attributes = raw_attributes
    else:
        attributes = raw_attributes

    if output_format == "csv":
        print_csv(attributes)
    elif output_format == "table":
        _print_table(attributes)
    else:
        print_json(attributes)


@attributes_app.command("show")
def show_attribute(
    attribute_id: int = typer.Argument(..., help="Attribute ID to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific attribute."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/attributes/view/{attribute_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            print_json(response)


@attributes_app.command("add")
def add_attribute(
    event_id: int = typer.Argument(..., help="Event ID to add attribute to"),
    attr_type: str = typer.Option(..., "-t", "--type", help="Attribute type"),
    value: str = typer.Option(..., "-v", "--value", help="Attribute value"),
    category: str = typer.Option(..., "-c", "--category", help="Attribute category"),
    comment: str | None = typer.Option(None, "-m", "--comment", help="Comment"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Add an attribute to an event."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    data: dict[str, Any] = {
        "type": attr_type,
        "value": value,
        "category": category,
    }
    if comment:
        data["comment"] = comment

    response = client.post_sync(f"/attributes/add/{event_id}", data={"Attribute": data})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        attr_id = response.get("Attribute", {}).get("id", "Unknown")
        typer.echo(f"Attribute added successfully: {attr_id}")


@attributes_app.command("edit")
def edit_attribute(
    attribute_id: int = typer.Argument(..., help="Attribute ID to edit"),
    value: str | None = typer.Option(None, "-v", "--value", help="New value"),
    comment: str | None = typer.Option(None, "-m", "--comment", help="New comment"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Edit an attribute."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    data: dict[str, Any] = {}
    if value:
        data["value"] = value
    if comment:
        data["comment"] = comment

    if not data:
        typer.echo("No changes specified", err=True)
        raise typer.Exit(1)

    response = client.post_sync(f"/attributes/edit/{attribute_id}", data={"Attribute": data})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Attribute {attribute_id} updated successfully")


@attributes_app.command("delete")
def delete_attribute(
    attribute_id: int = typer.Argument(..., help="Attribute ID to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Force deletion without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Delete an attribute."""
    from misp_cli.cli.app import get_app

    if not force:
        typer.confirm(f"Are you sure you want to delete attribute {attribute_id}?", abort=True)

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/attributes/delete/{attribute_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Attribute {attribute_id} deleted successfully")


@attributes_app.command("search")
def search_attributes(
    value: str = typer.Argument(..., help="Search value"),
    type: str | None = typer.Option(None, "-t", "--type", help="Filter by type"),
    category: str | None = typer.Option(None, "-c", "--category", help="Filter by category"),
    from_date: str | None = typer.Option(
        None, "--from", help="Start date filter (e.g., 2024-03-19, 2024-03-19T11:10:24Z, 7d)"
    ),
    to_date: str | None = typer.Option(
        None, "--to", help="End date filter (e.g., 2024-03-19, 2024-03-19T11:10:24Z, 14d)"
    ),
    last: str | None = typer.Option(
        None, "--last", help="Relative time filter (e.g., 5d, 12h, 30m, 1617875568)"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-T", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """Search for attributes by value."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    data: dict[str, Any] = {"value": value}
    if type:
        data["type"] = type
    if category:
        data["category"] = category
    if from_date:
        data["from"] = from_date
    if to_date:
        data["to"] = to_date
    if last:
        data["last"] = last

    response = client.post_sync("/attributes/restSearch", data=data)

    output_format = get_output_format(config, json_output, table_output, csv_output)

    # Unwrap nested Attribute structure: [{'Attribute': {...}}, ...] -> [{...}, ...]
    raw_attributes = response.get("attributes", response.get("data", []))
    if raw_attributes and isinstance(raw_attributes, list):
        # Check if each item is wrapped in "Attribute" key
        if all(isinstance(item, dict) and "Attribute" in item for item in raw_attributes):
            attributes = [item["Attribute"] for item in raw_attributes]
        else:
            attributes = raw_attributes
    else:
        attributes = raw_attributes

    if output_format == "csv":
        print_csv(attributes)
    elif output_format == "table":
        _print_table(attributes)
    else:
        print_json(attributes)


@attributes_app.command("types")
def list_attribute_types(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress non-essential output"),
):
    """List all available attribute types."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync("/attributes/describeTypes")
    result = response.get("result", {})

    # Extract types array from the response
    types = result.get("types", [])

    # If types is empty, try alternative extraction
    if not types:
        # Some MISP versions return types directly in response
        types = response.get("types", [])

    if config.output_format == "json" or json_output:
        print_json(types)
    else:
        if not quiet:
            typer.echo(f"Available attribute types ({len(types)} total):")
        for t in sorted(types):
            typer.echo(f"  - {t}")


@attributes_app.command("categories")
def list_attribute_categories(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List all available attribute categories."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    # Get types which includes category information
    response = client.get_sync("/attributes/describeTypes")
    result = response.get("result", {})
    categories = result.get("categories", [])

    if config.output_format == "json" or json_output:
        print_json(categories)
    else:
        typer.echo("Available attribute categories:")
        for c in categories:
            typer.echo(f"  - {c}")
