"""Tests for organisation management commands."""

import pytest
from unittest.mock import MagicMock, patch

from misp_cli.cli.commands.organisations import (
    list_organisations,
    show_organisation,
    create_organisation,
    edit_organisation,
    delete_organisation,
)


def setup_mock_app():
    """Set up a mock app for testing."""
    mock_config = MagicMock()
    mock_config.url = "https://misp.example.com"
    mock_config.api_key = "test-key"
    mock_config.verify_ssl = True
    mock_config.output_format = "json"

    mock_client = MagicMock()
    
    mock_console = MagicMock()

    mock_app = MagicMock()
    mock_app.profile = mock_config
    mock_app.client = mock_client
    mock_app.console = mock_console

    return mock_app, mock_config, mock_client


class TestOrganisationsCommands:
    """Tests for organisation commands."""

    def test_list_organisations(self):
        """Test listing organisations."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_response = [
            {
                "Organisation": {
                    "id": "1",
                    "name": "ORGNAME",
                    "uuid": "c99506a6-1255-4b71-afa5-7b8ba48c3b1b",
                    "local": True,
                    "nationality": "US",
                    "sector": "Technology",
                }
            }
        ]
        mock_client.get_sync.return_value = mock_response

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_organisations(limit=50, page=1, json_output=True, table_output=False)
            
            mock_client.get_sync.assert_called_once()
            call_args = mock_client.get_sync.call_args
            assert "/organisations" in call_args[0][0]

    def test_list_organisations_with_pagination(self):
        """Test listing organisations with pagination."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_response = []
        mock_client.get_sync.return_value = mock_response

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_organisations(limit=100, page=2, json_output=True, table_output=False)
            
            mock_client.get_sync.assert_called_once()
            call_args = mock_client.get_sync.call_args
            assert call_args[1]["params"]["limit"] == 100
            assert call_args[1]["params"]["page"] == 2

    def test_show_organisation(self):
        """Test showing organisation details."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_response = {
            "Organisation": {
                "id": "1",
                "name": "ORGNAME",
                "uuid": "c99506a6-1255-4b71-afa5-7b8ba48c3b1b",
                "description": "Test organisation",
                "local": True,
            }
        }
        mock_client.get_sync.return_value = mock_response

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            show_organisation(organisation_id="1", json_output=True, table_output=False)
            
            mock_client.get_sync.assert_called_once_with("/organisations/view/1")

    def test_show_organisation_by_uuid(self):
        """Test showing organisation by UUID."""
        mock_app, mock_config, mock_client = setup_mock_app()
        uuid = "c99506a6-1255-4b71-afa5-7b8ba48c3b1b"
        mock_response = {
            "Organisation": {
                "id": "1",
                "name": "ORGNAME",
                "uuid": uuid,
            }
        }
        mock_client.get_sync.return_value = mock_response

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            show_organisation(organisation_id=uuid, json_output=True, table_output=False)
            
            mock_client.get_sync.assert_called_once_with(f"/organisations/view/{uuid}")

    def test_create_organisation(self):
        """Test creating an organisation."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_response = {
            "Organisation": {
                "id": "123",
                "name": "New Org",
                "uuid": "c99506a6-1255-4b71-afa5-7b8ba48c3b1b",
            }
        }
        mock_client.post_sync.return_value = mock_response

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            create_organisation(
                name="New Org",
                description="Test organisation",
                type=None,
                nationality=None,
                sector="Technology",
                contacts=None,
                local=None,
                uuid=None,
                restricted_to_domain=None,
                json_output=True
            )
            
            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert "/admin/organisations/add" in call_args[0][0]
            data = call_args[1]["data"]
            assert data["name"] == "New Org"
            assert data["description"] == "Test organisation"
            assert data["sector"] == "Technology"

    def test_create_organisation_with_domain_restrictions(self):
        """Test creating an organisation with domain restrictions."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_response = {
            "Organisation": {
                "id": "123",
                "name": "Restricted Org",
            }
        }
        mock_client.post_sync.return_value = mock_response

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            create_organisation(
                name="Restricted Org",
                description=None,
                type=None,
                nationality=None,
                sector=None,
                contacts=None,
                local=None,
                uuid=None,
                restricted_to_domain="example.com,example.org",
                json_output=True
            )
            
            call_args = mock_client.post_sync.call_args
            data = call_args[1]["data"]
            assert data["restricted_to_domain"] == ["example.com", "example.org"]

    def test_edit_organisation(self):
        """Test editing an organisation."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_response = {
            "Organisation": {
                "id": "1",
                "name": "Updated Name",
                "sector": "Finance",
            }
        }
        mock_client.put_sync.return_value = mock_response

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            edit_organisation(
                organisation_id="1",
                name="Updated Name",
                description=None,
                type=None,
                nationality=None,
                sector="Finance",
                contacts=None,
                local=None,
                uuid=None,
                restricted_to_domain=None,
                json_output=True
            )
            
            mock_client.put_sync.assert_called_once()
            call_args = mock_client.put_sync.call_args
            assert "/admin/organisations/edit/1" in call_args[0][0]
            data = call_args[1]["data"]
            assert data["name"] == "Updated Name"
            assert data["sector"] == "Finance"

    def test_edit_organisation_no_fields(self):
        """Test editing organisation with no fields provided."""
        mock_app, mock_config, mock_client = setup_mock_app()

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            # typer.Exit raises click.exceptions.Exit, not SystemExit
            from click.exceptions import Exit
            with pytest.raises(Exit) as exc_info:
                edit_organisation(
                    organisation_id="1",
                    name=None,
                    description=None,
                    type=None,
                    nationality=None,
                    sector=None,
                    contacts=None,
                    local=None,
                    uuid=None,
                    restricted_to_domain=None,
                    json_output=True
                )
            
            assert exc_info.value.exit_code == 1

    def test_delete_organisation_force(self):
        """Test deleting organisation with force flag."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_response = {
            "saved": True,
            "success": True,
            "message": "Organisation deleted.",
        }
        mock_client.delete_sync.return_value = mock_response

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            delete_organisation(organisation_id="1", force=True, json_output=True)
            
            mock_client.delete_sync.assert_called_once_with("/admin/organisations/delete/1")

    def test_delete_organisation_failure(self):
        """Test failed organisation deletion."""
        mock_app, mock_config, mock_client = setup_mock_app()
        # Set output format to table to trigger error handling path
        mock_config.output_format = "table"
        mock_response = {
            "saved": False,
            "success": False,
            "message": "Organisation could not be deleted",
        }
        mock_client.delete_sync.return_value = mock_response

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            from click.exceptions import Exit
            with pytest.raises(Exit) as exc_info:
                delete_organisation(organisation_id="1", force=True, json_output=False)
            
            assert exc_info.value.exit_code == 1

    def test_list_organisations_table_format(self):
        """Test listing organisations in table format."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_response = [
            {
                "Organisation": {
                    "id": "1",
                    "name": "Org 1",
                    "uuid": "uuid-1",
                    "local": True,
                    "nationality": "US",
                    "sector": "Tech",
                }
            },
            {
                "Organisation": {
                    "id": "2",
                    "name": "Org 2",
                    "uuid": "uuid-2",
                    "local": False,
                    "nationality": "UK",
                    "sector": "Finance",
                }
            }
        ]
        mock_client.get_sync.return_value = mock_response

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_organisations(limit=50, page=1, json_output=False, table_output=True)
            
            mock_client.get_sync.assert_called_once()

    def test_create_organisation_minimal(self):
        """Test creating organisation with minimal required fields."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_response = {
            "Organisation": {
                "id": "123",
                "name": "Minimal Org",
            }
        }
        mock_client.post_sync.return_value = mock_response

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            create_organisation(
                name="Minimal Org",
                description=None,
                type=None,
                nationality=None,
                sector=None,
                contacts=None,
                local=None,
                uuid=None,
                restricted_to_domain=None,
                json_output=True
            )
            
            mock_client.post_sync.assert_called_once()
