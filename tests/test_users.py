"""Tests for user commands."""

import pytest
from unittest.mock import MagicMock, patch

from misp_cli.cli.commands.users import (
    list_users,
    show_user,
    current_user,
    create_user,
    edit_user,
    delete_user,
    list_org_users,
    admin_user,
    disable_user,
    enable_user,
)


def setup_mock_app():
    """Set up a mock app for testing."""
    mock_config = MagicMock()
    mock_config.url = "https://misp.example.com"
    mock_config.api_key = "test-key"
    mock_config.verify_ssl = True
    mock_config.output_format = "json"

    mock_client = MagicMock()

    mock_app = MagicMock()
    mock_app.profile = mock_config
    mock_app.client = mock_client

    return mock_app, mock_config, mock_client


class TestUsersCommands:
    """Tests for user commands."""

    def test_list_users_json_output(self):
        """Test listing users with JSON output."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {
            "User": [
                {"id": 1, "email": "user1@example.com", "org_id": 1, "role_id": 1},
                {"id": 2, "email": "user2@example.com", "org_id": 1, "role_id": 2}
            ]
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_users(limit=50, page=1, json_output=True, table_output=False)

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert "/admin/users/index" in call_args[0][0]
            assert call_args[1]["data"]["limit"] == 50

    def test_show_user_json_output(self):
        """Test showing a user with JSON output."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "User": {"id": 1, "email": "user@example.com", "org_id": 1, "role_id": 1}
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            show_user(user_id=1, json_output=True)

            mock_client.get_sync.assert_called_once_with("/users/view/1")

    def test_current_user(self):
        """Test getting current user information."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "User": {"id": 42, "email": "current@example.com", "org_id": 1, "role_id": 3}
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            current_user(json_output=True)

            mock_client.get_sync.assert_called_once_with("/users/view/me")

    def test_create_user(self):
        """Test creating a new user."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {
            "User": {"id": 42, "email": "new@example.com", "org_id": 1, "role_id": 2}
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            create_user(
                email="new@example.com",
                org_id=1,
                role_id=2,
                first_name="New",
                last_name="User",
                password="password123",
                confirm_password="password123",
                json_output=True
            )

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert "/users/add" in call_args[0][0]
            assert call_args[1]["data"]["User"]["email"] == "new@example.com"
            assert call_args[1]["data"]["User"]["org_id"] == 1
            assert call_args[1]["data"]["User"]["role_id"] == 2

    def test_edit_user(self):
        """Test editing a user."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "User updated"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            edit_user(
                user_id=1,
                email="updated@example.com",
                org_id=None,
                role_id=None,
                first_name=None,
                last_name=None,
                password=None,
                json_output=True
            )

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert "/users/edit/1" in call_args[0][0]
            assert call_args[1]["data"]["User"]["email"] == "updated@example.com"

    def test_delete_user_with_force(self):
        """Test deleting a user with force flag."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "User deleted"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            delete_user(user_id=1, force=True, json_output=True)

            mock_client.post_sync.assert_called_once_with("/users/delete/1")

    def test_list_org_users(self):
        """Test listing users in an organisation."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {
            "User": [
                {"id": 1, "email": "user1@example.com", "org_id": 5},
                {"id": 2, "email": "user2@example.com", "org_id": 5}
            ]
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_org_users(org_id=5, json_output=True, table_output=False)

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert "/admin/users/index" in call_args[0][0]
            assert call_args[1]["data"]["org_id"] == 5

    def test_admin_user_enable(self):
        """Test making a user an admin."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "User made admin"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            admin_user(user_id=1, enable=True, disable=False, json_output=True)

            mock_client.post_sync.assert_called_once_with("/users/admin/1")

    def test_admin_user_disable(self):
        """Test removing admin status from a user."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "User removed from admin"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            admin_user(user_id=1, enable=False, disable=True, json_output=True)

            mock_client.post_sync.assert_called_once_with("/users/removeadmin/1")

    def test_disable_user(self):
        """Test disabling a user."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "User disabled"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            disable_user(user_id=1, force=True, json_output=True)

            mock_client.post_sync.assert_called_once_with("/users/disable/1")

    def test_enable_user(self):
        """Test enabling a user."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "User enabled"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            enable_user(user_id=1, json_output=True)

            mock_client.post_sync.assert_called_once_with("/users/enable/1")

    def test_list_users_error_handling(self):
        """Test error handling when listing users fails."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.side_effect = Exception("API Error")

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            with pytest.raises(Exception):
                list_users(limit=50, page=1, json_output=True, table_output=False)
