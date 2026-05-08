"""Galaxy management commands for MISP CLI."""

from typing import Any

import typer
from rich.table import Table

from misp_cli.cli.output import get_output_format, print_csv, print_json

galaxies_app = typer.Typer(
    name="galaxies",
    help="Manage MISP galaxies",
    add_help_option=True,
    invoke_without_command=True,
)


@galaxies_app.callback()
def galaxies_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP galaxies."""
    # Show help if requested or no subcommand given
    if help or ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


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


@galaxies_app.command("list")
def list_galaxies(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of galaxies"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress non-essential output"),
):
    """List all galaxies."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    params: dict[str, Any] = {}
    if limit:
        params["limit"] = limit

    response = client.post_sync("/galaxies/index", data=params)

    output_format = get_output_format(config, json_output, table_output, csv_output)

    # Unwrap nested Galaxy structure: [{'Galaxy': {...}}, ...] -> [{...}, ...]
    raw_galaxies = response.get("galaxies", response.get("data", []))
    if raw_galaxies and isinstance(raw_galaxies, list):
        # Check if each item is wrapped in "Galaxy" key
        if all(isinstance(item, dict) and "Galaxy" in item for item in raw_galaxies):
            galaxies = [item["Galaxy"] for item in raw_galaxies]
        else:
            galaxies = raw_galaxies
    else:
        galaxies = raw_galaxies

    # Client-side limit fallback when API ignores pagination
    if limit and len(galaxies) > limit:
        galaxies = galaxies[:limit]

    if not quiet:
        typer.echo(f"Found {len(galaxies)} galaxy(ies)")

    if output_format == "csv":
        print_csv(galaxies)
    elif output_format == "table":
        _print_table(galaxies)
    else:
        print_json(galaxies)


@galaxies_app.command("show")
def show_galaxy(
    galaxy_id: int = typer.Argument(..., help="Galaxy ID to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific galaxy."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/galaxies/view/{galaxy_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            print_json(response)


@galaxies_app.command("elements")
def list_elements(
    galaxy_id: int = typer.Argument(..., help="Galaxy ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """List elements of a galaxy."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync("/galaxy_clusters/index", data={"galaxy_id": galaxy_id})

    output_format = get_output_format(config, json_output, table_output, csv_output)
    raw = response.get("GalaxyCluster", response.get("galaxy_clusters", response.get("data", [])))
    if isinstance(raw, list) and raw and isinstance(raw[0], dict) and "GalaxyCluster" in raw[0]:
        elements = [item["GalaxyCluster"] for item in raw]
    else:
        elements = raw if isinstance(raw, list) else []

    if output_format == "csv":
        print_csv(elements)
    elif output_format == "table":
        _print_table(elements)
    else:
        print_json(elements)


@galaxies_app.command("cluster")
def show_cluster(
    cluster_id: int = typer.Argument(..., help="Cluster ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific cluster."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/galaxy_clusters/view/{cluster_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            print_json(response)


@galaxies_app.command("search")
def search_galaxies(
    term: str = typer.Argument(..., help="Search term"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """Search galaxies."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync("/galaxies/index", data={"searchall": term})

    output_format = get_output_format(config, json_output, table_output, csv_output)

    # Unwrap nested Galaxy structure: [{'Galaxy': {...}}, ...] -> [{...}, ...]
    raw_galaxies = response.get("galaxies", response.get("data", []))
    if raw_galaxies and isinstance(raw_galaxies, list):
        # Check if each item is wrapped in "Galaxy" key
        if all(isinstance(item, dict) and "Galaxy" in item for item in raw_galaxies):
            galaxies = [item["Galaxy"] for item in raw_galaxies]
        else:
            galaxies = raw_galaxies
    else:
        galaxies = raw_galaxies

    if output_format == "csv":
        print_csv(galaxies)
    elif output_format == "table":
        _print_table(galaxies)
    else:
        print_json(galaxies)


@galaxies_app.command("attach")
def attach_cluster(
    event_id: int = typer.Argument(..., help="Event ID"),
    cluster_id: int = typer.Option(..., "-c", "--cluster-id", help="Cluster ID to attach"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Attach a galaxy cluster to an event."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(
        f"/events/attachCluster/{event_id}", data={"GalaxyCluster": {"id": cluster_id}}
    )

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo("Cluster attached successfully")


@galaxies_app.command("detach")
def detach_cluster(
    event_id: int = typer.Argument(..., help="Event ID"),
    cluster_id: int = typer.Option(..., "-c", "--cluster-id", help="Cluster ID to detach"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Detach a galaxy cluster from an event."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.post_sync(
        f"/events/detachCluster/{event_id}", data={"GalaxyCluster": {"id": cluster_id}}
    )

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        typer.echo("Cluster detached successfully")


@galaxies_app.command("event-galaxies")
def list_event_galaxies(
    event_id: int = typer.Argument(..., help="Event ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """List galaxies attached to an event."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/events/view/{event_id}", params={"galaxy": 1})

    output_format = get_output_format(config, json_output, table_output, csv_output)
    event = response.get("Event", response)
    galaxies = event.get("Galaxy", [])

    if output_format == "csv":
        print_csv(galaxies)
    elif output_format == "table":
        _print_table(galaxies)
    else:
        print_json(galaxies)
