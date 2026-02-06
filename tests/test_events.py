"""Tests for event commands."""

import pytest
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
        mock_client.get.return_value = {
            "events": [{"id": 1, "info": "Test Event"}]
        }
        
        with patch("misp_cli.cli.commands.events.MISPConfig") as mock_config_class:
            with patch("misp_cli.cli.commands.events.MISPCLient") as mock_client_class:
                mock_config_class.from_file.return_value = mock_config
                mock_client_class.return_value = mock_client
                
                # Test that the client is called correctly
                events_app.callback()  # Initialize
                
                # Call the list function directly
                from misp_cli.cli.commands.events import list_events
                list_events(limit=50, page=1, search=None, org=None, json_output=True, table_output=False)
                
                mock_client.get.assert_called_once()
                call_args = mock_client.get.call_args
                assert call_args[0][0] == "/events/index"
                assert call_args[1]["params"]["limit"] == 50

    def test_events_show_json_output(self):
        """Test showing an event with JSON output."""
        mock_config = MagicMock()
        mock_config.url = "https://misp.example.com"
        mock_config.api_key = "test-key"
        mock_config.verify_ssl = True
        mock_config.output_format = "json"
        
        mock_client = MagicMock()
        mock_client.get.return_value = {
            "Event": {"id": 1, "info": "Test Event"}
        }
        
        with patch("misp_cli.cli.commands.events.MISPConfig") as mock_config_class:
            with patch("misp_cli.cli.commands.events.MISPCLient") as mock_client_class:
                mock_config_class.from_file.return_value = mock_config
                mock_client_class.return_value = mock_client
                
                from misp_cli.cli.commands.events import show_event
                show_event(event_id=1, context=False, json_output=True, table_output=False)
                
                mock_client.get.assert_called_once_with("/events/view/1", params={})

    def test_events_create_json_output(self):
        """Test creating an event with JSON output."""
        mock_config = MagicMock()
        mock_config.url = "https://misp.example.com"
        mock_config.api_key = "test-key"
        mock_config.verify_ssl = True
        mock_config.output_format = "json"
        
        mock_client = MagicMock()
        mock_client.post.return_value = {
            "Event": {"id": 42, "info": "New Event"}
        }
        
        with patch("misp_cli.cli.commands.events.MISPConfig") as mock_config_class:
            with patch("misp_cli.cli.commands.events.MISPCLient") as mock_client_class:
                mock_config_class.from_file.return_value = mock_config
                mock_client_class.return_value = mock_client
                
                from misp_cli.cli.commands.events import create_event
                create_event(
                    info="New Event",
                    threat_level=2,
                    analysis=1,
                    distribution=5,
                    event_date=None,
                    json_output=True
                )
                
                mock_client.post.assert_called_once()
                call_args = mock_client.post.call_args
                assert "/events/add" in call_args[0][0]

    def test_events_delete_force(self):
        """Test deleting an event with force flag."""
        mock_config = MagicMock()
        mock_config.url = "https://misp.example.com"
        mock_config.api_key = "test-key"
        mock_config.verify_ssl = True
        mock_config.output_format = "json"
        
        mock_client = MagicMock()
        mock_client.post.return_value = {"message": "Event deleted"}
        
        with patch("misp_cli.cli.commands.events.MISPConfig") as mock_config_class:
            with patch("misp_cli.cli.commands.events.MISPCLient") as mock_client_class:
                mock_config_class.from_file.return_value = mock_config
                mock_client_class.return_value = mock_client
                
                from misp_cli.cli.commands.events import delete_event
                delete_event(event_id=1, force=True, json_output=True)
                
                mock_client.post.assert_called_once_with("/events/delete/1")

    def test_events_publish(self):
        """Test publishing an event."""
        mock_config = MagicMock()
        mock_config.url = "https://misp.example.com"
        mock_config.api_key = "test-key"
        mock_config.verify_ssl = True
        mock_config.output_format = "json"
        
        mock_client = MagicMock()
        mock_client.post.return_value = {"message": "Event published"}
        
        with patch("misp_cli.cli.commands.events.MISPConfig") as mock_config_class:
            with patch("misp_cli.cli.commands.events.MISPCLient") as mock_client_class:
                mock_config_class.from_file.return_value = mock_config
                mock_client_class.return_value = mock_client
                
                from misp_cli.cli.commands.events import publish_event
                publish_event(event_id=1, json_output=True)
                
                mock_client.post.assert_called_once_with("/events/publish/1")

    def test_events_search(self):
        """Test searching events."""
        mock_config = MagicMock()
        mock_config.url = "https://misp.example.com"
        mock_config.api_key = "test-key"
        mock_config.verify_ssl = True
        mock_config.output_format = "json"
        
        mock_client = MagicMock()
        mock_client.post.return_value = {
            "events": [{"id": 1, "info": "Ransomware Event"}]
        }
        
        with patch("misp_cli.cli.commands.events.MISPConfig") as mock_config_class:
            with patch("misp_cli.cli.commands.events.MISPCLient") as mock_client_class:
                mock_config_class.from_file.return_value = mock_config
                mock_client_class.return_value = mock_client
                
                from misp_cli.cli.commands.events import search_events
                search_events(term="ransomware", json_output=True, table_output=False)
                
                mock_client.post.assert_called_once()
                call_args = mock_client.post.call_args
                assert "/events/restSearch" in call_args[0][0]
