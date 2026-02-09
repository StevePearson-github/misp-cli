"""Statistics commands for MISP CLI."""

import typer

from misp_cli.cli.output import print_json

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


@stats_app.command("system")
def stats_system():
    """Get system statistics."""
    from misp_cli.cli.app import get_app

    app = get_app()
    client = app.client

    response = client.get_sync("/users/statistics/data.json")
    print_json(response)


@stats_app.command("users")
def stats_users():
    """Get user statistics."""
    from misp_cli.cli.app import get_app

    app = get_app()
    client = app.client

    response = client.get_sync("/users/statistics.json")
    print_json(response)


@stats_app.command("orgs")
def stats_orgs():
    """Get organisation statistics."""
    from misp_cli.cli.app import get_app

    app = get_app()
    client = app.client

    response = client.get_sync("/users/statistics/orgs.json")
    print_json(response)


@stats_app.command("tags")
def stats_tags():
    """Get tag statistics."""
    from misp_cli.cli.app import get_app

    app = get_app()
    client = app.client

    response = client.get_sync("/users/statistics/tags.json")
    print_json(response)
