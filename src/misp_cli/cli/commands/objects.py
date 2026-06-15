"""MISP Object management commands for MISP CLI."""

import json
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

objects_app = typer.Typer(
    name="objects",
    help="Manage MISP objects",
    add_help_option=True,
    invoke_without_command=True,
)


@objects_app.callback()
def objects_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP objects."""
    # Show help if requested or no subcommand given
    if help or ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


@objects_app.command("list")
def list_objects(
    event_id: int | None = typer.Option(None, "-e", "--event", help="Filter by event ID"),
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of objects"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    from_date: str | None = typer.Option(
        None, "--from", help="Start date filter (e.g., 2024-03-19, 2024-03-19T11:10:24Z, 7d)"
    ),
    to_date: str | None = typer.Option(
        None, "--to", help="End date filter (e.g., 2024-03-19, 2024-03-19T11:10:24Z, 14d)"
    ),
    date: str | None = typer.Option(None, "--date", help="Date filter (YYYY-MM-DD)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
    count: bool = COUNT_OPTION,
):
    """List all objects."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    effective_limit = 0 if count is True else limit
    params: dict[str, Any] = {"page": page}
    if effective_limit:
        params["limit"] = effective_limit
    if event_id:
        params["eventid"] = event_id
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    if date:
        params["date"] = date

    response = client.get_sync("/objects/restSearch", params=params)

    output_format = get_output_format(config, json_output, table_output, csv_output)
    objects = response.get("objects", response.get("data", []))

    if count is True:
        print_count(objects, json_output)

    if output_format == "csv":
        print_csv(objects)
    elif output_format == "table":
        print_table(objects)
    else:
        print_json(objects)


@objects_app.command("show")
def show_object(
    object_id: int = typer.Argument(..., help="Object ID to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific object."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/objects/view/{object_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        if isinstance(response, dict):
            print_table([response])
        else:
            print_json(response)


@objects_app.command("add")
def add_object(
    event_id: int = typer.Argument(..., help="Event ID to add object to"),
    object_name: str = typer.Option(..., "-n", "--name", help="Object name"),
    template_id: int = typer.Option(..., "-t", "--template-id", help="Object template ID"),
    comment: str | None = typer.Option(None, "-c", "--comment", help="Comment"),
    attributes: str | None = typer.Option(None, "-a", "--attributes", help="JSON attributes"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Add an object to an event."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    import asyncio

    attr_list = json.loads(attributes) if attributes else None

    async def _add(c: Any) -> dict[str, Any]:
        template_data = await c.get(f"/objectTemplates/view/{template_id}")
        template_info = template_data.get("ObjectTemplate", template_data)
        obj_data: dict[str, Any] = {
            "Object": {
                "name": object_name,
                "template_id": template_id,
                "template_uuid": template_info.get("uuid", ""),
                "template_version": template_info.get("version", 1),
                "meta-category": template_info.get("meta-category", ""),
                "comment": comment or "",
            }
        }
        if attr_list:
            obj_data["Attribute"] = attr_list
        return await c.post(f"/objects/add/{event_id}", data=obj_data)

    response = asyncio.run(_add(client))

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        obj_id = response.get("Object", {}).get("id", "Unknown")
        typer.echo(f"Object created successfully: {obj_id}")


@objects_app.command("edit")
def edit_object(
    object_id: int = typer.Argument(..., help="Object ID to edit"),
    name: str | None = typer.Option(None, "-n", "--name", help="New name"),
    comment: str | None = typer.Option(None, "-c", "--comment", help="New comment"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Edit an object."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    data: dict[str, Any] = {}
    if name:
        data["name"] = name
    if comment is not None:
        data["comment"] = comment

    if not data:
        typer.echo("No changes specified", err=True)
        raise typer.Exit(1)

    response = client.post_sync(f"/objects/edit/{object_id}", data={"Object": data})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Object {object_id} updated successfully")


@objects_app.command("delete")
def delete_object(
    object_id: int = typer.Argument(..., help="Object ID to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Force deletion without confirmation"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Delete an object."""
    from misp_cli.cli.app import get_app

    if not force:
        typer.confirm(f"Are you sure you want to delete object {object_id}?", abort=True)

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(f"/objects/delete/{object_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo(f"Object {object_id} deleted successfully")


@objects_app.command("references")
def list_references(
    object_id: int = typer.Argument(..., help="Object ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """List references for an object."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/objects/view/{object_id}", params={"references": 1})

    output_format = get_output_format(config, json_output, table_output, csv_output)
    obj = response.get("Object", response)
    references = obj.get("ObjectReference", [])

    if output_format == "csv":
        print_csv(references)
    elif output_format == "table":
        print_table(references)
    else:
        print_json(references)


@objects_app.command("add-reference")
def add_reference(
    object_id: int = typer.Argument(..., help="Source object ID"),
    referenced_object_id: int = typer.Option(..., "-r", "--ref-id", help="Referenced object ID"),
    relationship_type: str = typer.Option(..., "-t", "--type", help="Relationship type"),
    comment: str | None = typer.Option(None, "-c", "--comment", help="Comment"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Add a reference to an object."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    data: dict[str, Any] = {
        "referenced_object_id": referenced_object_id,
        "relationship_type": relationship_type,
        "comment": comment or "",
    }

    response = client.post_sync(
        f"/objectReferences/add/{object_id}", data={"ObjectReference": data}
    )

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo("Object reference added successfully")


@objects_app.command("event-objects")
def list_event_objects(
    event_id: int = typer.Argument(..., help="Event ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """List all objects for an event."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/events/view/{event_id}", params={"objects": 1})

    output_format = get_output_format(config, json_output, table_output, csv_output)
    event = response.get("Event", response)
    objects = event.get("Object", [])

    if output_format == "csv":
        print_csv(objects)
    elif output_format == "table":
        print_table(objects)
    else:
        print_json(objects)
