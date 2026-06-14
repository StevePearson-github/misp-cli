"""Tests for attribute commands."""

import pytest
from unittest.mock import MagicMock, patch

from misp_cli.cli.commands.attributes import (
    list_attributes,
    show_attribute,
    add_attribute,
    edit_attribute,
    delete_attribute,
    search_attributes,
    list_attribute_types,
    list_attribute_categories,
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


class TestAttributesCommands:
    """Tests for attribute commands."""

    def test_list_attributes_json_output(self):
        """Test listing attributes with JSON output."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "attributes": [
                {"id": 1, "type": "ip-src", "value": "192.168.1.1", "category": "Network activity"},
                {"id": 2, "type": "domain", "value": "example.com", "category": "Network activity"}
            ]
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_attributes(event_id=None, type=None, category=None, limit=50, page=1, json_output=True, table_output=False)

            mock_client.get_sync.assert_called_once()
            call_args = mock_client.get_sync.call_args
            assert call_args[0][0] == "/attributes/index"
            assert call_args[1]["params"]["limit"] == 50
            assert call_args[1]["params"]["page"] == 1

    def test_list_attributes_with_event_filter(self):
        """Test listing attributes with event_id filter."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "attributes": [{"id": 1, "type": "ip-src", "value": "192.168.1.1"}]
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_attributes(event_id=42, type=None, category=None, limit=50, page=1, json_output=True, table_output=False)

            mock_client.get_sync.assert_called_once()
            call_args = mock_client.get_sync.call_args
            assert call_args[1]["params"]["eventid"] == 42

    def test_show_attribute_json_output(self):
        """Test showing an attribute with JSON output."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "Attribute": {"id": 1, "type": "ip-src", "value": "192.168.1.1", "category": "Network activity"}
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            show_attribute(attribute_id=1, json_output=True)

            mock_client.get_sync.assert_called_once_with("/attributes/view/1")

    def test_add_attribute(self):
        """Test adding an attribute."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {
            "Attribute": {"id": 123, "type": "ip-src", "value": "10.0.0.1"}
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            add_attribute(
                event_id=1,
                attr_type="ip-src",
                value="10.0.0.1",
                category="Network activity",
                comment=None,
                json_output=True
            )

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert "/attributes/add/1" in call_args[0][0]
            assert call_args[1]["data"]["Attribute"]["type"] == "ip-src"
            assert call_args[1]["data"]["Attribute"]["value"] == "10.0.0.1"

    def test_edit_attribute(self):
        """Test editing an attribute."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "Attribute updated"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            edit_attribute(attribute_id=1, value="192.168.1.2", comment="Updated IP", json_output=True)

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert "/attributes/edit/1" in call_args[0][0]
            assert call_args[1]["data"]["Attribute"]["value"] == "192.168.1.2"
            assert call_args[1]["data"]["Attribute"]["comment"] == "Updated IP"

    def test_delete_attribute_with_force(self):
        """Test deleting an attribute with force flag."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "Attribute deleted"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            delete_attribute(attribute_id=1, force=True, json_output=True)

            mock_client.post_sync.assert_called_once_with("/attributes/delete/1")

    def test_search_attributes(self):
        """Test searching attributes."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {
            "attributes": [{"id": 1, "type": "ip-src", "value": "10.0.0.1"}]
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            search_attributes(value="10.0.0.1", type=None, category=None, json_output=True, table_output=False)

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert "/attributes/restSearch" in call_args[0][0]
            assert call_args[1]["data"]["value"] == "10.0.0.1"

    def test_list_attribute_types(self):
        """Test listing attribute types."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "result": {
                "types": ["ip-src", "domain", "email-src", "hostname"]
            }
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_attribute_types(json_output=True)

            mock_client.get_sync.assert_called_once_with("/attributes/describeTypes")

    def test_list_attribute_categories(self):
        """Test listing attribute categories."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "result": {
                "categories": ["Network activity", "Financial fraud", "Payload delivery"]
            }
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_attribute_categories(json_output=True)

            mock_client.get_sync.assert_called_once_with("/attributes/describeTypes")

    def test_list_attributes_count(self):
        """Test that --count returns count and exits without limit in request."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "attributes": [{"id": 1, "type": "ip-src", "value": "1.1.1.1", "category": "Network activity"}]
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            with pytest.raises(Exception):
                list_attributes(
                    event_id=None, type=None, category=None, limit=50, page=1,
                    json_output=True, table_output=False, count=True
                )

        call_args = mock_client.get_sync.call_args
        assert "limit" not in call_args[1]["params"]

    def test_list_attributes_error_handling(self):
        """Test error handling when listing attributes fails."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.side_effect = Exception("API Error")

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            with pytest.raises(Exception):
                list_attributes(event_id=None, type=None, category=None, limit=50, page=1, json_output=True, table_output=False)
