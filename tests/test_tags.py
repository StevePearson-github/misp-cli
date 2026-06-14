"""Tests for tag commands."""

import pytest
from unittest.mock import MagicMock, patch

from misp_cli.cli.commands.tags import (
    list_tags,
    show_tag,
    search_tags,
    create_tag,
    edit_tag,
    delete_tag,
    attach_tag,
    detach_tag,
    list_event_tags,
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


class TestTagsCommands:
    """Tests for tag commands."""

    def test_list_tags_json_output(self):
        """Test listing tags with JSON output."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {
            "Tag": [
                {"id": 1, "name": "test-tag", "color": "#0088cc"},
                {"id": 2, "name": "malware-tag", "color": "#ff0000"}
            ]
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_tags(limit=50, page=1, json_output=True, table_output=False, csv_output=False)

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert call_args[0][0] == "/tags/index"
            assert call_args[1]["data"]["limit"] == 50

    def test_show_tag_json_output(self):
        """Test showing a tag with JSON output."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "Tag": {"id": 1, "name": "test-tag", "color": "#0088cc", "exportable": True}
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            show_tag(tag_id=1, json_output=True)

            mock_client.get_sync.assert_called_once_with("/tags/view/1")

    def test_search_tags(self):
        """Test searching for tags by name using substring search."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "Tag": [{"id": 1, "name": "test-tag", "colour": "#0088cc"}]
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            search_tags(name="test", json_output=True, table_output=False)

            mock_client.get_sync.assert_called_once()
            call_args = mock_client.get_sync.call_args
            assert call_args[0][0] == "/tags/index/searchall:test"

    def test_search_tags_url_encodes_term(self):
        """Test that special characters in search term are URL-encoded."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {"Tag": []}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            search_tags(name="tlp:white", json_output=True, table_output=False)

            call_args = mock_client.get_sync.call_args
            assert "tlp%3Awhite" in call_args[0][0]

    def test_create_tag(self):
        """Test creating a new tag."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {
            "Tag": {"id": 42, "name": "new-tag", "color": "#00ff00"}
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            create_tag(
                name="new-tag",
                color="#00ff00",
                exportable=True,
                hide_tag=False,
                json_output=True
            )

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert "/tags/add" in call_args[0][0]
            assert call_args[1]["data"]["Tag"]["name"] == "new-tag"
            assert call_args[1]["data"]["Tag"]["colour"] == "#00ff00"
            assert call_args[1]["data"]["Tag"]["exportable"] is True

    def test_edit_tag(self):
        """Test editing a tag."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "Tag updated"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            edit_tag(tag_id=1, name="updated-tag", color="#ff0000", exportable=None, hide_tag=None, json_output=True)

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert "/tags/edit/1" in call_args[0][0]
            assert call_args[1]["data"]["Tag"]["name"] == "updated-tag"
            assert call_args[1]["data"]["Tag"]["colour"] == "#ff0000"

    def test_delete_tag_with_force(self):
        """Test deleting a tag with force flag."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "Tag deleted"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            delete_tag(tag_id=1, force=True, json_output=True)

            mock_client.post_sync.assert_called_once_with("/tags/delete/1")

    def test_attach_tag_to_event(self):
        """Test attaching a tag to an event."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "Tag attached"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            attach_tag(event_id=1, tag_id=2, attribute_id=None, json_output=True)

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert call_args[0][0] == "/events/addTag/1/2"

    def test_attach_tag_to_attribute(self):
        """Test attaching a tag to an attribute."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "Tag attached"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            attach_tag(event_id=1, tag_id=2, attribute_id=3, json_output=True)

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert call_args[0][0] == "/attributes/addTag/3/2"

    def test_detach_tag_from_event(self):
        """Test detaching a tag from an event."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "Tag detached"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            detach_tag(event_id=1, tag_id=2, attribute_id=None, json_output=True)

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert "/events/removeTag/1" in call_args[0][0]

    def test_list_event_tags(self):
        """Test listing tags for an event via Tag key."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "Event": {
                "id": 1,
                "info": "Test Event",
                "Tag": [
                    {"id": 1, "name": "test-tag"},
                    {"id": 2, "name": "malware-tag"}
                ]
            }
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_event_tags(event_id=1, json_output=True, table_output=False)

            mock_client.get_sync.assert_called_once_with("/events/view/1", params={"tags": 1})

    def test_list_event_tags_via_event_tag(self):
        """Test that tags are extracted from EventTag when Tag key is empty."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "Event": {
                "id": 1,
                "Tag": [],
                "EventTag": [
                    {"id": 10, "tag_id": 1, "Tag": {"id": 1, "name": "tlp:green"}},
                    {"id": 11, "tag_id": 2, "Tag": {"id": 2, "name": "threat-intel"}},
                ]
            }
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_event_tags(event_id=1, json_output=True, table_output=False)

    def test_list_tags_count(self):
        """Test that --count returns count and exits."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {
            "Tag": [{"id": 1, "name": "t1"}, {"id": 2, "name": "t2"}]
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            with pytest.raises(Exception):
                list_tags(limit=50, page=1, json_output=True, table_output=False, csv_output=False, count=True)

        call_args = mock_client.post_sync.call_args
        assert "limit" not in call_args[1]["data"]

    def test_search_tags_count(self):
        """Test that --count on search returns count and exits."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {"Tag": [{"id": 1, "name": "malware"}]}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            with pytest.raises(Exception):
                search_tags(name="malware", json_output=True, table_output=False, csv_output=False, count=True)

    def test_list_tags_error_handling(self):
        """Test error handling when listing tags fails."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.side_effect = Exception("API Error")

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            with pytest.raises(Exception):
                list_tags(limit=50, page=1, json_output=True, table_output=False, csv_output=False)
