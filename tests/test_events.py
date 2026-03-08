"""Tests for event commands."""

from unittest.mock import MagicMock, patch

from misp_cli.cli.commands.events import events_app


class TestEventsCommands:
    """Tests for event commands."""

    def test_events_list_json_output(self):
        """Test listing events with JSON output."""
        mock_config = MagicMock()
        mock_config.url = "https://misp.example.com"
        mock_config.api_key = "test-key"
        mock_config.verify_ssl = True
        mock_config.output_format = "json"

        mock_client = MagicMock()
        mock_client.post_sync.return_value = {
            "response": [{"id": 1, "info": "Test Event"}]
        }

        mock_app = MagicMock()
        mock_app.profile = mock_config
        mock_app.client = mock_client

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):

                # Test that the client is called correctly
                events_app.callback()  # Initialize

                # Call the list function directly
                from misp_cli.cli.commands.events import list_events
                list_events(limit=50, page=1, search=None, org=None, json_output=True, table_output=False)

                mock_client.post_sync.assert_called_once()
                call_args = mock_client.post_sync.call_args
                assert call_args[0][0] == "/events/restSearch"
                assert call_args[1]["data"]["limit"] == 50

    def test_events_show_json_output(self):
        """Test showing an event with JSON output."""
        mock_config = MagicMock()
        mock_config.url = "https://misp.example.com"
        mock_config.api_key = "test-key"
        mock_config.verify_ssl = True
        mock_config.output_format = "json"

        mock_client = MagicMock()
        mock_client.get_sync.return_value = {
            "Event": {"id": 1, "info": "Test Event"}
        }

        mock_app = MagicMock()
        mock_app.profile = mock_config
        mock_app.client = mock_client

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):

                from misp_cli.cli.commands.events import show_event
                show_event(event_id=1, context=False, json_output=True, table_output=False)

                mock_client.get_sync.assert_called_once_with("/events/view/1", params={})

    def test_events_create_json_output(self):
        """Test creating an event with JSON output."""
        mock_config = MagicMock()
        mock_config.url = "https://misp.example.com"
        mock_config.api_key = "test-key"
        mock_config.verify_ssl = True
        mock_config.output_format = "json"

        mock_client = MagicMock()
        mock_client.post_sync.return_value = {
            "Event": {"id": 42, "info": "New Event"}
        }

        mock_app = MagicMock()
        mock_app.profile = mock_config
        mock_app.client = mock_client

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):

                from misp_cli.cli.commands.events import create_event
                create_event(
                    info="New Event",
                    threat_level=2,
                    analysis=1,
                    distribution=5,
                    event_date=None,
                    json_output=True
                )

                mock_client.post_sync.assert_called_once()
                call_args = mock_client.post_sync.call_args
                assert "/events/add" in call_args[0][0]

    def test_events_delete_force(self):
        """Test deleting an event with force flag."""
        mock_config = MagicMock()
        mock_config.url = "https://misp.example.com"
        mock_config.api_key = "test-key"
        mock_config.verify_ssl = True
        mock_config.output_format = "json"

        mock_client = MagicMock()
        mock_client.post_sync.return_value = {"message": "Event deleted"}

        mock_app = MagicMock()
        mock_app.profile = mock_config
        mock_app.client = mock_client

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):

                from misp_cli.cli.commands.events import delete_event
                delete_event(event_id=1, force=True, json_output=True)

                mock_client.post_sync.assert_called_once_with("/events/delete/1")

    def test_events_publish(self):
        """Test publishing an event."""
        mock_config = MagicMock()
        mock_config.url = "https://misp.example.com"
        mock_config.api_key = "test-key"
        mock_config.verify_ssl = True
        mock_config.output_format = "json"

        mock_client = MagicMock()
        mock_client.post_sync.return_value = {"message": "Event published"}

        mock_app = MagicMock()
        mock_app.profile = mock_config
        mock_app.client = mock_client

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):

                from misp_cli.cli.commands.events import publish_event
                publish_event(event_id=1, json_output=True)

                mock_client.post_sync.assert_called_once_with("/events/publish/1")

    def test_events_search(self):
        """Test searching events."""
        mock_config = MagicMock()
        mock_config.url = "https://misp.example.com"
        mock_config.api_key = "test-key"
        mock_config.verify_ssl = True
        mock_config.output_format = "json"

        mock_client = MagicMock()
        mock_client.post_sync.return_value = {
            "events": [{"id": 1, "info": "Ransomware Event"}]
        }

        mock_app = MagicMock()
        mock_app.profile = mock_config
        mock_app.client = mock_client

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):

                from misp_cli.cli.commands.events import search_events
                search_events(term="ransomware", json_output=True, table_output=False)

                mock_client.post_sync.assert_called_once()
                call_args = mock_client.post_sync.call_args
                assert "/events/restSearch" in call_args[0][0]

    def test_events_list_org_filter(self):
        """Test that org filter uses org parameter."""
        mock_config = MagicMock()
        mock_config.url = "https://misp.example.com"
        mock_config.api_key = "test-key"
        mock_config.verify_ssl = True
        mock_config.output_format = "json"

        mock_client = MagicMock()
        mock_client.post_sync.return_value = {
            "response": [{"id": 1, "info": "Test Event", "Orgc": {"name": "ACME Corp"}}]
        }

        mock_app = MagicMock()
        mock_app.profile = mock_config
        mock_app.client = mock_client

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):

            from misp_cli.cli.commands.events import list_events
            list_events(limit=50, page=1, search=None, org="ACME Corp", json_output=True, table_output=False)

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert call_args[0][0] == "/events/restSearch"
            assert call_args[1]["data"]["org"] == "ACME Corp"
