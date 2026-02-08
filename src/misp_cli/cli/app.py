"""Command-line interface for MISP CLI."""

import sys
from typing import Optional
from pathlib import Path
from rich.console import Console
import typer
from misp_cli.core.config import ConfigManager, CLIConfig
from misp_cli.core.client import MISPCLient
from misp_cli.core.exceptions import MISPConfigurationError


app = typer.Typer(
    name="misp-cli",
    help="MISP CLI - Command-line interface for MISP",
    add_completion=False,
    add_help_option=True,
)


class MISPApp:
    """
    Main application class managing CLI state and dependencies.
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        profile: Optional[str] = None,
        output_format: Optional[str] = None,
        no_color: bool = False,
    ):
        self.console = Console(no_color=no_color)
        self.output_format = output_format

        # Load configuration
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load()

        # Get active profile
        profile_name = profile or self.config.default_profile
        if profile_name not in self.config.profiles:
            raise MISPConfigurationError(f"Profile '{profile_name}' not found in configuration")

        self.profile = self.config.profiles[profile_name]

        # Create MISP client
        self.client = MISPCLient(
            base_url=self.profile.url,
            api_key=self.profile.api_key,
            verify_ssl=self.profile.verify_ssl,
            timeout=self.profile.timeout,
        )

    def get_output_format(self) -> str:
        """Get the output format."""
        return self.output_format or self.profile.output_format


# Global app instance
_misp_app: Optional[MISPApp] = None


def get_app() -> MISPApp:
    """Get the global MISP app instance."""
    global _misp_app
    if _misp_app is None:
        raise MISPConfigurationError("CLI app not initialized")
    return _misp_app


def set_app(app: MISPApp):
    """Set the global MISP app instance."""
    global _misp_app
    _misp_app = app


@app.callback()
def callback(
    ctx: typer.Context,
    config: Optional[Path] = typer.Option(
        None,
        "-c",
        "--config",
        help="Path to configuration file",
        exists=False,
        dir_okay=False,
    ),
    profile: Optional[str] = typer.Option(
        None,
        "-p",
        "--profile",
        help="Profile name to use from configuration",
    ),
    output: Optional[str] = typer.Option(
        None,
        "-o",
        "--output",
        help="Output format (json, table, csv)",
    ),
    no_color: bool = typer.Option(
        False,
        "--no-color",
        help="Disable colored output",
    ),
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
        callback=lambda ctx, value: ctx.get_help() if value and not ctx.resilient_parsing else None,
    ),
):
    """MISP CLI - Command-line interface for MISP."""
    # Skip initialization for config --generate
    if "config" in sys.argv and "--generate" in sys.argv:
        return
    
    # Check if help was requested
    if help and not ctx.resilient_parsing:
        typer.echo(ctx.get_help())
        raise typer.Exit()
    
    # Skip initialization during help/parsing
    if ctx.resilient_parsing:
        return
    
    try:
        misp_app = MISPApp(
            config_path=config,
            profile=profile,
            output_format=output,
            no_color=no_color,
        )
        set_app(misp_app)
    except MISPConfigurationError as e:
        # Show configuration error and exit
        typer.echo(f"Configuration error: {e.message}", err=True)
        raise typer.Exit(2)


@app.command("version")
def version(
    ctx: typer.Context,
    help: bool = typer.Option(False, "-h", "--help", help="Show this help message", is_eager=True),
):
    """Show the MISP server version."""
    if help:
        typer.echo(ctx.get_help())
        raise typer.Exit()
    
    from misp_cli.cli.app import get_app
    
    app = get_app()
    client = app.client
    
    response = client.get_sync("/servers/getVersion")
    typer.echo(response)


@app.command("config")
def config_command(
    ctx: typer.Context,
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    validate: bool = typer.Option(False, "--validate", help="Validate configuration file"),
    generate: bool = typer.Option(False, "--generate", help="Generate default config file"),
    help: bool = typer.Option(False, "-h", "--help", help="Show this help message", is_eager=True),
):
    """Manage MISP CLI configuration."""
    if help:
        typer.echo(ctx.get_help())
        raise typer.Exit()
    
    # Handle generate separately as it doesn't require existing config
    if generate:
        try:
            config_manager = ConfigManager()
            path = config_manager.create_default_config()
            typer.echo(f"Default configuration file created: {path}")
            typer.echo("Please update with your MISP instance details.")
            return
        except Exception as e:
            typer.echo(f"Failed to create config: {e}", err=True)
            raise typer.Exit(2)
    
    app = get_app()

    if show:
        typer.echo(f"Default profile: {app.config.default_profile}")
        typer.echo(f"Available profiles: {', '.join(app.config.profiles.keys())}")
        for name, profile in app.config.profiles.items():
            typer.echo(f"\n[{name}]")
            typer.echo(f"  url: {profile.url}")
            typer.echo(f"  verify_ssl: {profile.verify_ssl}")
            typer.echo(f"  timeout: {profile.timeout}")
            typer.echo(f"  output_format: {profile.output_format}")

    elif validate:
        try:
            app.config_manager.validate()
            typer.echo("Configuration is valid")
        except MISPConfigurationError as e:
            typer.echo(f"Configuration error: {e.message}", err=True)
            raise typer.Exit(2)


def main():
    """Main entry point."""
    # Commands are already registered at module level
    app()


# Register all command subapps at module level for proper help display
def _register_commands():
    """Register all command subapps."""
    from misp_cli.cli.commands.events import events_app
    from misp_cli.cli.commands.attributes import attributes_app
    from misp_cli.cli.commands.users import users_app
    from misp_cli.cli.commands.tags import tags_app
    from misp_cli.cli.commands.sharing_groups import sharing_groups_app
    from misp_cli.cli.commands.feeds import feeds_app
    from misp_cli.cli.commands.servers import servers_app
    from misp_cli.cli.commands.objects import objects_app
    from misp_cli.cli.commands.object_templates import object_templates_app
    from misp_cli.cli.commands.galaxies import galaxies_app
    from misp_cli.cli.commands.warninglists import warninglists_app
    from misp_cli.cli.commands.noticelists import noticelists_app
    from misp_cli.cli.commands.taxonomies import taxonomies_app
    from misp_cli.cli.commands.roles import roles_app
    from misp_cli.cli.commands.decaying_models import decaying_models_app
    from misp_cli.cli.commands.event_blocklists import event_blocklists_app
    from misp_cli.cli.commands.attribute_blocklists import attribute_blocklists_app
    from misp_cli.cli.commands.news import news_app
    from misp_cli.cli.commands.feeds_manage_feeds import manage_feeds_app
    
    # Add command groups
    app.add_typer(events_app, name="events")
    app.add_typer(attributes_app, name="attributes")
    app.add_typer(users_app, name="users")
    app.add_typer(tags_app, name="tags")
    app.add_typer(sharing_groups_app, name="sharing-groups")
    app.add_typer(feeds_app, name="feeds")
    app.add_typer(servers_app, name="servers")
    app.add_typer(objects_app, name="objects")
    app.add_typer(object_templates_app, name="object-templates")
    app.add_typer(galaxies_app, name="galaxies")
    app.add_typer(warninglists_app, name="warninglists")
    app.add_typer(noticelists_app, name="noticelists")
    app.add_typer(taxonomies_app, name="taxonomies")
    app.add_typer(roles_app, name="roles")
    app.add_typer(decaying_models_app, name="decaying-models")
    app.add_typer(event_blocklists_app, name="event-blocklists")
    app.add_typer(attribute_blocklists_app, name="attribute-blocklists")
    app.add_typer(news_app, name="news")
    app.add_typer(manage_feeds_app, name="manage-feeds")

# Register commands when module is imported
_register_commands()


if __name__ == "__main__":
    main()
