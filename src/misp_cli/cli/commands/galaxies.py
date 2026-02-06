"""Galaxy management commands for MISP CLI."""

import json
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table

from misp_cli.core.config import MISPProfile

galaxies_app = typer.Typer(
    name="galaxies",
    help="Manage MISP galaxies",
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


@galaxies_app.command("list")
def list_galaxies(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of galaxies"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List all galaxies."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    params: Dict[str, Any] = {
        "limit": limit,
        "page": page,
    }
    
    response = client.get_sync("/galaxies/index", params=params)
    
    output_format = _get_output_format(config, json_output, table_output)
    galaxies = response.get("galaxies", response.get("data", []))
    
    if output_format == "table":
        _print_table(galaxies)
    else:
        _print_json(galaxies)


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
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            _print_json(response)


@galaxies_app.command("elements")
def list_elements(
    galaxy_id: int = typer.Argument(..., help="Galaxy ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List elements of a galaxy."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/galaxies/view/{galaxy_id}", params={"elements": 1})
    
    output_format = _get_output_format(config, json_output, table_output)
    galaxy = response.get("Galaxy", response)
    elements = galaxy.get("GalaxyCluster", [])
    
    if output_format == "table":
        _print_table(elements)
    else:
        _print_json(elements)


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
    
    response = client.get_sync(f"/galaxies/cluster/{cluster_id}")
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        if isinstance(response, dict):
            _print_table([response])
        else:
            _print_json(response)


@galaxies_app.command("search")
def search_galaxies(
    term: str = typer.Argument(..., help="Search term"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Search galaxies."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync("/galaxies/index", params={"search": term})
    
    output_format = _get_output_format(config, json_output, table_output)
    galaxies = response.get("galaxies", response.get("data", []))
    
    if output_format == "table":
        _print_table(galaxies)
    else:
        _print_json(galaxies)


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
        f"/events/attachCluster/{event_id}",
        data={"GalaxyCluster": {"id": cluster_id}}
    )
    
    if config.output_format == "json" or json_output:
        _print_json(response)
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
        f"/events/detachCluster/{event_id}",
        data={"GalaxyCluster": {"id": cluster_id}}
    )
    
    if config.output_format == "json" or json_output:
        _print_json(response)
    else:
        typer.echo("Cluster detached successfully")


@galaxies_app.command("event-galaxies")
def list_event_galaxies(
    event_id: int = typer.Argument(..., help="Event ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """List galaxies attached to an event."""
    from misp_cli.cli.app import get_app
    
    app = get_app()
    config = app.profile
    client = app.client
    
    response = client.get_sync(f"/events/view/{event_id}", params={"galaxy": 1})
    
    output_format = _get_output_format(config, json_output, table_output)
    event = response.get("Event", response)
    galaxies = event.get("Galaxy", [])
    
    if output_format == "table":
        _print_table(galaxies)
    else:
        _print_json(galaxies)
