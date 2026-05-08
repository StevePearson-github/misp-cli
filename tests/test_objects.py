"""Tests for object commands."""

import json
from unittest.mock import MagicMock, patch

from misp_cli.cli.commands.objects import add_object, list_objects, show_object


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


class TestAddObject:
    def test_add_object_body_structure_no_attributes(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"Object": {"id": 42, "name": "domain-ip"}}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            add_object(
                event_id=1,
                object_name="domain-ip",
                template_id=54,
                comment=None,
                attributes=None,
                json_output=True,
            )

        call_args = mock_client.post_sync.call_args
        assert call_args[0][0] == "/objects/add/1"
        body = call_args[1]["data"]
        assert "Object" in body
        assert body["Object"]["name"] == "domain-ip"
        assert body["Object"]["template_id"] == 54
        assert "Attribute" not in body
        assert "attributes" not in body.get("Object", {})

    def test_add_object_attributes_at_top_level(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"Object": {"id": 42}}

        attrs = [{"object_relation": "ip", "value": "1.2.3.4", "type": "ip-dst"}]

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            add_object(
                event_id=1,
                object_name="domain-ip",
                template_id=54,
                comment="test",
                attributes=json.dumps(attrs),
                json_output=True,
            )

        body = mock_client.post_sync.call_args[1]["data"]
        assert "Attribute" in body
        assert body["Attribute"] == attrs
        assert "attributes" not in body.get("Object", {})


class TestListObjects:
    def test_list_objects_json_output(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {"objects": [{"id": 1, "name": "domain-ip"}]}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_objects(
                event_id=None,
                limit=50,
                page=1,
                from_date=None,
                to_date=None,
                date=None,
                json_output=True,
                table_output=False,
                csv_output=False,
            )

        mock_client.get_sync.assert_called_once()
        assert mock_client.get_sync.call_args[0][0] == "/objects/restSearch"


class TestShowObject:
    def test_show_object_json_output(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {"Object": {"id": 1, "name": "domain-ip"}}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            show_object(object_id=1, json_output=True)

        mock_client.get_sync.assert_called_once_with("/objects/view/1")
