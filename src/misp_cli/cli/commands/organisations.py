"""Organisation management commands for MISP CLI."""

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

organisations_app = typer.Typer(
    name="organisations",
    help="Manage MISP organisations",
    add_help_option=True,
    invoke_without_command=True,
)


@organisations_app.callback()
def organisations_callback(
    ctx: typer.Context,
    help: bool = typer.Option(
        False,
        "-h",
        "--help",
        help="Show this help message",
        is_eager=True,
    ),
):
    """Manage MISP organisations."""
    # Show help if requested or no subcommand given
    if help or ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


@organisations_app.command("list")
def list_organisations(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of organisations"),
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    count: bool = COUNT_OPTION,
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
    csv_output: bool = typer.Option(False, "--csv", help="Output as CSV"),
):
    """List all organisations.

    Retrieves a list of organisations from the MISP instance.

    Examples:
        misp-cli organisations list
        misp-cli organisations list --limit 100 --table
        misp-cli organisations list --json
    """
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    effective_limit = 0 if count is True else limit
    params: dict[str, Any] = {"page": page}
    if effective_limit:
        params["limit"] = effective_limit

    response = client.get_sync("/organisations/index/scope:all", params=params)

    output_format = get_output_format(config, json_output, table_output, csv_output)

    # Handle response - can be a list directly or wrapped in response key
    if isinstance(response, list):
        orgs = response
    else:
        orgs = response.get(
            "Organisation", response.get("organisations/index/scope:all", response.get("data", []))
        )

    # Extract Organisation data if wrapped
    if orgs and isinstance(orgs[0], dict) and "Organisation" in orgs[0]:
        orgs = [item["Organisation"] for item in orgs]

    if count is True:
        print_count(orgs, json_output, output_format)

    if output_format == "csv":
        print_csv(orgs)
    elif output_format == "table":
        # Select key columns for table display
        table_data = []
        for org in orgs:
            table_data.append(
                {
                    "id": org.get("id", ""),
                    "name": org.get("name", ""),
                    "uuid": org.get("uuid", ""),
                    "local": org.get("local", ""),
                    "nationality": org.get("nationality", ""),
                    "sector": org.get("sector", ""),
                }
            )
        print_table(table_data)
    else:
        print_json(orgs)


@organisations_app.command("show")
def show_organisation(
    organisation_id: str = typer.Argument(..., help="Organisation ID or UUID to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
):
    """Show details of a specific organisation.

    Retrieves detailed information about a specific organisation by ID or UUID.

    Examples:
        misp-cli organisations show 1
        misp-cli organisations show c99506a6-1255-4b71-afa5-7b8ba48c3b1b
        misp-cli organisations show 1 --json
    """
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    response = client.get_sync(f"/organisations/view/{organisation_id}")

    output_format = get_output_format(config, json_output, table_output)

    # Extract Organisation data if wrapped
    org_data = response
    if isinstance(response, dict) and "Organisation" in response:
        org_data = response["Organisation"]

    if output_format == "table":
        print_table([org_data])
    else:
        print_json(org_data)


@organisations_app.command("create")
def create_organisation(
    name: str = typer.Option(..., "-n", "--name", help="Organisation name"),
    description: str | None = typer.Option(
        None, "-d", "--description", help="Organisation description"
    ),
    type: str | None = typer.Option(
        None, "-t", "--type", help="Organisation type (e.g., ADMIN, Commercial, Educational)"
    ),
    nationality: str | None = typer.Option(None, "--nationality", help="Organisation nationality"),
    sector: str | None = typer.Option(None, "-s", "--sector", help="Organisation sector"),
    contacts: str | None = typer.Option(None, "-c", "--contacts", help="Organisation contacts"),
    local: bool | None = typer.Option(None, "--local", help="Whether the organisation is local"),
    uuid: str | None = typer.Option(None, "--uuid", help="Organisation UUID"),
    restricted_to_domain: str | None = typer.Option(
        None, "--restricted-to-domain", help="Comma-separated list of domains to restrict to"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Create a new organisation.

    Creates a new organisation in the MISP instance. Requires admin privileges.

    Examples:
        misp-cli organisations create --name "ACME Corp" --sector "Technology"
        misp-cli organisations create -n "Example Org" -d "Test organisation" --type "Commercial"
        misp-cli organisations create -n "Local Org" --local --restricted-to-domain "example.com,example.org"
    """
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    data: dict[str, Any] = {
        "name": name,
    }

    if description:
        data["description"] = description
    if type:
        data["type"] = type
    if nationality:
        data["nationality"] = nationality
    if sector:
        data["sector"] = sector
    if contacts:
        data["contacts"] = contacts
    if local is not None:
        data["local"] = local
    if uuid:
        data["uuid"] = uuid
    if restricted_to_domain:
        # Convert comma-separated string to list
        data["restricted_to_domain"] = [d.strip() for d in restricted_to_domain.split(",")]

    response = client.post_sync("/admin/organisations/add", data=data)

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        # Extract organisation data from response
        org_data = response
        if isinstance(response, dict) and "Organisation" in response:
            org_data = response["Organisation"]

        org_id = org_data.get("id", "Unknown")
        org_name = org_data.get("name", name)
        typer.echo(f"Organisation created successfully: {org_name} (ID: {org_id})")


@organisations_app.command("edit")
def edit_organisation(
    organisation_id: str = typer.Argument(..., help="Organisation ID or UUID to edit"),
    name: str | None = typer.Option(None, "-n", "--name", help="New organisation name"),
    description: str | None = typer.Option(
        None, "-d", "--description", help="New organisation description"
    ),
    type: str | None = typer.Option(
        None, "-t", "--type", help="New organisation type (e.g., ADMIN, Commercial, Educational)"
    ),
    nationality: str | None = typer.Option(
        None, "--nationality", help="New organisation nationality"
    ),
    sector: str | None = typer.Option(None, "-s", "--sector", help="New organisation sector"),
    contacts: str | None = typer.Option(None, "-c", "--contacts", help="New organisation contacts"),
    local: bool | None = typer.Option(None, "--local", help="Whether the organisation is local"),
    uuid: str | None = typer.Option(None, "--uuid", help="Organisation UUID"),
    restricted_to_domain: str | None = typer.Option(
        None, "--restricted-to-domain", help="Comma-separated list of domains to restrict to"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Edit an organisation.

    Updates an existing organisation in the MISP instance. Requires admin privileges.
    Only the fields provided will be updated.

    Examples:
        misp-cli organisations edit 1 --name "New Name"
        misp-cli organisations edit 1 -d "Updated description" --sector "Finance"
        misp-cli organisations edit c99506a6-1255-4b71-afa5-7b8ba48c3b1b --nationality "US"
        misp-cli organisations edit 1 --restricted-to-domain "example.com,example.org"
    """
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    data: dict[str, Any] = {}

    if name:
        data["name"] = name
    if description is not None:
        data["description"] = description
    if type:
        data["type"] = type
    if nationality is not None:
        data["nationality"] = nationality
    if sector is not None:
        data["sector"] = sector
    if contacts is not None:
        data["contacts"] = contacts
    if local is not None:
        data["local"] = local
    if uuid:
        data["uuid"] = uuid
    if restricted_to_domain is not None:
        # Convert comma-separated string to list
        data["restricted_to_domain"] = (
            [d.strip() for d in restricted_to_domain.split(",")] if restricted_to_domain else []
        )

    if not data:
        typer.echo("Error: No fields provided to update", err=True)
        raise typer.Exit(1)

    response = client.put_sync(f"/admin/organisations/edit/{organisation_id}", data=data)

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        # Extract organisation data from response
        org_data = response
        if isinstance(response, dict) and "Organisation" in response:
            org_data = response["Organisation"]

        org_id = org_data.get("id", organisation_id)
        org_name = org_data.get("name", "Unknown")
        typer.echo(f"Organisation edited successfully: {org_name} (ID: {org_id})")


@organisations_app.command("delete")
def delete_organisation(
    organisation_id: str = typer.Argument(..., help="Organisation ID or UUID to delete"),
    force: bool = typer.Option(False, "-f", "--force", help="Skip confirmation prompt"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Delete an organisation.

    Deletes an organisation from the MISP instance. Requires admin privileges.
    This action cannot be undone.

    Examples:
        misp-cli organisations delete 1
        misp-cli organisations delete c99506a6-1255-4b71-afa5-7b8ba48c3b1b --force
        misp-cli organisations delete 1 --json
    """
    from misp_cli.cli.app import get_app

    app = get_app()
    config = app.profile
    client = app.client

    # Confirm deletion unless force flag is set
    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete organisation {organisation_id}?")
        if not confirm:
            typer.echo("Deletion cancelled")
            raise typer.Exit(0)

    response = client.delete_sync(f"/admin/organisations/delete/{organisation_id}")

    if config.output_format == "json" or json_output:
        print_json(response)
    else:
        if isinstance(response, dict):
            if response.get("saved") or response.get("success"):
                typer.echo(f"Organisation deleted successfully: {organisation_id}")
            else:
                error_msg = response.get("message", response.get("errors", "Unknown error"))
                typer.echo(f"Failed to delete organisation: {error_msg}", err=True)
                raise typer.Exit(1)
        else:
            typer.echo(f"Organisation deleted successfully: {organisation_id}")
