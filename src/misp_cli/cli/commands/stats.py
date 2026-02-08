"""Statistics commands for MISP CLI."""

import typer

from misp_cli.cli.output import get_output_format, print_csv, print_json, print_table

stats_app = typer.Typer(
    name="stats",
    help="View MISP statistics",
    add_help_option=True,
    invoke_without_command=True,
)


@stats_app.callback()
def stats_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """View MISP statistics."""
    if help:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@stats_app.command("overview")
def stats_overview(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Show overall statistics overview."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync("/stats")

    output_format = get_output_format(config, json_output, table_output, False)

    if output_format == "table":
        print_table([response])
    else:
        print_json(response)


@stats_app.command("attributes")
def stats_attributes(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Show attribute statistics."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync("/stats/attributes")

    output_format = get_output_format(config, json_output, table_output, False)

    if output_format == "table":
        print_table([response])
    else:
        print_json(response)


@stats_app.command("events")
def stats_events(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Show event statistics."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync("/stats/events")

    output_format = get_output_format(config, json_output, table_output, False)

    if output_format == "table":
        print_table([response])
    else:
        print_json(response)


@stats_app.command("users")
def stats_users(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Show user statistics."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync("/stats/users")

    output_format = get_output_format(config, json_output, table_output, False)

    if output_format == "table":
        print_table([response])
    else:
        print_json(response)


@stats_app.command("organisations")
def stats_organisations(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Show organisation statistics."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync("/stats/organisations")

    output_format = get_output_format(config, json_output, table_output, False)

    if output_format == "table":
        print_table([response])
    else:
        print_json(response)


@stats_app.command("tags")
def stats_tags(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Show tag statistics."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync("/stats/tags")

    output_format = get_output_format(config, json_output, table_output, False)

    if output_format == "table":
        print_table([response])
    else:
        print_json(response)


@stats_app.command("galaxies")
def stats_galaxies(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Show galaxy statistics."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync("/stats/galaxies")

    output_format = get_output_format(config, json_output, table_output, False)

    if output_format == "table":
        print_table([response])
    else:
        print_json(response)


@stats_app.command("attack")
def stats_attack(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Show ATT&CK statistics."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync("/stats/attackMatrix")

    output_format = get_output_format(config, json_output, table_output, False)

    if output_format == "table":
        print_table([response])
    else:
        print_json(response)


@stats_app.command("sightings")
def stats_sightings(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Show sighting statistics."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync("/stats/sightings")

    output_format = get_output_format(config, json_output, table_output, False)

    if output_format == "table":
        print_table([response])
    else:
        print_json(response)


@stats_app.command("correlation")
def stats_correlation(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Show correlation statistics."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync("/stats/correlations")

    output_format = get_output_format(config, json_output, table_output, False)

    if output_format == "table":
        print_table([response])
    else:
        print_json(response)


@stats_app.command("health")
def stats_health(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Show instance health statistics."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync("/stats/health")

    output_format = get_output_format(config, json_output, table_output, False)

    if output_format == "table":
        print_table([response])
    else:
        print_json(response)


@stats_app.command("workers")
def stats_workers(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Show background worker statistics."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync("/stats/workers")

    output_format = get_output_format(config, json_output, table_output, False)

    if output_format == "table":
        print_table([response])
    else:
        print_json(response)


@stats_app.command("dashboard")
def stats_dashboard(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Show dashboard statistics."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync("/stats/getDashboards")

    output_format = get_output_format(config, json_output, table_output, False)

    if output_format == "table":
        print_table([response])
    else:
        print_json(response)


@stats_app.command("export")
def stats_export(
    stats_type: str = typer.Argument(..., help="Type of statistics to export"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """Export statistics in various formats."""
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    valid_types = ["events", "attributes", "tags", "users", "organisations", "galaxies"]
    if stats_type not in valid_types:
        typer.echo(f"Invalid type: {stats_type}. Valid types: {', '.join(valid_types)}", err=True)
        raise typer.Exit(1)

    response = client.get_sync(f"/stats/export/{stats_type}")

    output_format = get_output_format(config, json_output, False, csv_output)

    if output_format == "csv":
        print_csv(response.get("data", response))
    elif output_format == "table":
        print_table(response.get("data", [response]))
    else:
        print_json(response)
