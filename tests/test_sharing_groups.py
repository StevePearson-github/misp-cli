"""Tests for sharing group commands."""

from unittest.mock import MagicMock, patch

from misp_cli.cli.commands.sharing_groups import (
    add_organization,
    remove_organization,
    add_server,
    remove_server,
    list_sharing_groups,
    show_sharing_group,
)


def setup_mock_app():
    mock_config = MagicMock()
    mock_config.url = "https://misp.example.com"
    mock_config.api_key = "test-key"
    mock_config.verify_ssl = True
    mock_config.output_format = "json"

    mock_client = MagicMock()

    mock_app = MagicMock()
    mock_app.profile = mock_config
    mock_app.client = mock_client
    mock_app.console = MagicMock()

    return mock_app, mock_config, mock_client


class TestAddOrganization:
    def test_add_org_uses_get_path(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {"saved": True}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            add_organization(sharing_group_id=1, org_id=3, json_output=True)

        mock_client.get_sync.assert_called_once_with("/sharing_groups/addOrg/1/3")
        mock_client.post_sync.assert_not_called()

    def test_add_org_encodes_ids_in_path(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            add_organization(sharing_group_id=10, org_id=42, json_output=True)

        assert mock_client.get_sync.call_args[0][0] == "/sharing_groups/addOrg/10/42"


class TestRemoveOrganization:
    def test_remove_org_uses_get_path(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {"saved": True}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            remove_organization(sharing_group_id=1, org_id=3, json_output=True)

        mock_client.get_sync.assert_called_once_with("/sharing_groups/removeOrg/1/3")
        mock_client.post_sync.assert_not_called()


class TestAddServer:
    def test_add_server_uses_get_path(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {"saved": True}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            add_server(sharing_group_id=1, server_id=5, json_output=True)

        mock_client.get_sync.assert_called_once_with("/sharing_groups/addServer/1/5")
        mock_client.post_sync.assert_not_called()


class TestRemoveServer:
    def test_remove_server_uses_get_path(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {"saved": True}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            remove_server(sharing_group_id=1, server_id=5, json_output=True)

        mock_client.get_sync.assert_called_once_with("/sharing_groups/removeServer/1/5")
        mock_client.post_sync.assert_not_called()


class TestListSharingGroups:
    def test_list_sharing_groups_json_output(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {"sharing_groups": [{"id": 1, "name": "SG1"}]}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_sharing_groups(
                limit=50, page=1, json_output=True, table_output=False, csv_output=False
            )

        mock_client.get_sync.assert_called_once()
        assert mock_client.get_sync.call_args[0][0] == "/sharing_groups/index"


class TestShowSharingGroup:
    def test_show_sharing_group_json_output(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {"SharingGroup": {"id": 1, "name": "SG1"}}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            show_sharing_group(sharing_group_id=1, json_output=True)

        mock_client.get_sync.assert_called_once_with("/sharing_groups/view/1")
