"""Tag management commands for MISP CLI."""

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

tags_app = typer.Typer(
    name="tags",
    help="Manage MISP tags",
    add_help_option=True,
    invoke_without_command=True,
)


@tags_app.callback()
def tags_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP tags."""
    # Show help if requested or no subcommand given
    if help or ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


@tags_app.command("list")
def list_tags(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of tags"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
    count: bool = COUNT_OPTION,
):
    """List all tags."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    effective_limit = 0 if count is True else limit
    data: dict[str, Any] = {"page": page}
    if effective_limit:
        data["limit"] = effective_limit

    response = client.post_sync("/tags/index", data=data)

    output_format = get_output_format(config, json_output, table_output, csv_output)
    tags = response.get("Tag", response.get("tags", response.get("data", [])))

    # Client-side limit fallback when API ignores pagination
    if effective_limit and len(tags) > effective_limit:
        tags = tags[:effective_limit]

    if count is True:
        print_count(tags, json_output)

    if output_format == "csv":
        print_csv(tags)
    elif output_format == "table":
        print_table(tags)
    else:
        print_json(tags)


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
        print_json(response)
    else:
        if isinstance(response, dict):
            print_table([response])
        else:
            print_json(response)


@tags_app.command("search")
def search_tags(
    name: str = typer.Argument(..., help="Tag name to search for"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
    count: bool = COUNT_OPTION,
):
    """Search for tags by name."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    import urllib.parse

    encoded_name = urllib.parse.quote(name, safe="")
    response = client.get_sync(f"/tags/index/searchall:{encoded_name}")

    output_format = get_output_format(config, json_output, table_output, csv_output)
    tags = response.get("Tag", response.get("tags", response.get("data", [])))

    if count is True:
        print_count(tags, json_output)

    if output_format == "csv":
        print_csv(tags)
    elif output_format == "table":
        print_table(tags)
    else:
        print_json(tags)


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

    data: dict[str, Any] = {
        "name": name,
        "colour": color,
        "exportable": exportable,
    }
    if hide_tag:
        data["hide_tag"] = hide_tag

    response = client.post_sync("/tags/add", data={"Tag": data})

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        tag_id = response.get("Tag", {}).get("id", "Unknown")
        typer.echo(f"Tag created successfully: {tag_id}")


@tags_app.command("edit")
def edit_tag(
    tag_id: int = typer.Argument(..., help="Tag ID to edit"),
    name: str | None = typer.Option(None, "-n", "--name", help="New tag name"),
    color: str | None = typer.Option(None, "-c", "--color", help="New tag color"),
    exportable: bool | None = typer.Option(None, "-e", "--exportable", help="Exportable tag"),
    hide_tag: bool | None = typer.Option(None, "--hide", help="Hide tag from export"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Edit a tag."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    data: dict[str, Any] = {}
    if name:
        data["name"] = name
    if color:
        data["colour"] = color
    if exportable is not None:
        data["exportable"] = exportable
    if hide_tag is not None:
        data["hide_tag"] = hide_tag

    if not data:
        typer.echo("No changes specified", err=True)
        raise typer.Exit(1)

    response = client.post_sync(f"/tags/edit/{tag_id}", data={"Tag": data})

    if config.output_format == "json" or json_output:
        print_json(response)
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
        print_json(response)
    else:
        typer.echo(f"Tag {tag_id} deleted successfully")


@tags_app.command("attach")
def attach_tag(
    event_id: int = typer.Argument(..., help="Event ID"),
    tag_id: int = typer.Option(..., "-t", "--tag-id", help="Tag ID to attach"),
    attribute_id: int | None = typer.Option(
        None, "-a", "--attribute-id", help="Attribute ID (optional)"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Attach a tag to an event or attribute."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    if attribute_id:
        response = client.post_sync(f"/attributes/addTag/{attribute_id}/{tag_id}")
    else:
        response = client.post_sync(f"/events/addTag/{event_id}/{tag_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo("Tag attached successfully")


@tags_app.command("detach")
def detach_tag(
    event_id: int = typer.Argument(..., help="Event ID"),
    tag_id: int = typer.Option(..., "-t", "--tag-id", help="Tag ID to detach"),
    attribute_id: int | None = typer.Option(
        None, "-a", "--attribute-id", help="Attribute ID (optional)"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Detach a tag from an event or attribute."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    if attribute_id:
        response = client.post_sync(f"/attributes/removeTag/{attribute_id}/{tag_id}")
    else:
        response = client.post_sync(f"/events/removeTag/{event_id}/{tag_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
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

    output_format = get_output_format(config, json_output, table_output)
    event = response.get("Event", response)
    tags = event.get("Tag", [])
    if not tags:
        tags = [et["Tag"] for et in event.get("EventTag", []) if "Tag" in et]

    if output_format == "table":
        print_table(tags)
    else:
        print_json(tags)
