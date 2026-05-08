"""Tests for galaxy commands."""

from unittest.mock import MagicMock, patch

import pytest

from misp_cli.cli.commands.galaxies import (
    list_galaxies,
    show_galaxy,
    list_elements,
    show_cluster,
    search_galaxies,
    attach_cluster,
    detach_cluster,
    list_event_galaxies,
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
    mock_app.console = MagicMock()

    return mock_app, mock_config, mock_client


class TestListGalaxies:
    """Tests for list_galaxies command."""

    def test_list_galaxies_json_output(self):
        """Test listing galaxies with JSON output."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {
            "galaxies": [
                {"id": 1, "name": "Galaxy 1", "namespace": "threat-intel"},
                {"id": 2, "name": "Galaxy 2", "namespace": "mitre-attack"}
            ]
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_galaxies(
                limit=50, json_output=True, table_output=False, csv_output=False, quiet=False
            )

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert call_args[0][0] == "/galaxies/index"

    def test_list_galaxies_with_limit(self):
        """Test listing galaxies with custom limit."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"galaxies": []}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_galaxies(
                limit=100, json_output=True, table_output=False, csv_output=False, quiet=False
            )

            call_args = mock_client.post_sync.call_args
            assert call_args[1]["data"]["limit"] == 100

    def test_list_galaxies_quiet_mode(self):
        """Test listing galaxies with quiet mode."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"galaxies": [{"id": 1, "name": "Galaxy 1"}]}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_galaxies(
                limit=50, json_output=True, table_output=False, csv_output=False, quiet=True
            )

            # Should not raise, quiet mode suppresses output

    def test_list_galaxies_unwrap_nested(self):
        """Test that nested Galaxy structure is properly unwrapped."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {
            "galaxies": [
                {"Galaxy": {"id": 1, "name": "Galaxy 1"}},
                {"Galaxy": {"id": 2, "name": "Galaxy 2"}}
            ]
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_galaxies(
                limit=50, json_output=True, table_output=False, csv_output=False, quiet=False
            )

            mock_client.post_sync.assert_called_once()


class TestShowGalaxy:
    """Tests for show_galaxy command."""

    def test_show_galaxy_json_output(self):
        """Test showing a galaxy with JSON output."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "Galaxy": {"id": 1, "name": "Test Galaxy", "description": "Test description"}
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            show_galaxy(galaxy_id=1, json_output=True)

            mock_client.get_sync.assert_called_once_with("/galaxies/view/1")


class TestListElements:
    """Tests for list_elements command."""

    def test_list_elements_json_output(self):
        """Test listing galaxy elements via galaxy_clusters/index."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {
            "GalaxyCluster": [
                {"id": 1, "value": "Cluster 1"},
                {"id": 2, "value": "Cluster 2"}
            ]
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_elements(
                galaxy_id=1, json_output=True, table_output=False, csv_output=False
            )

            mock_client.post_sync.assert_called_once_with(
                "/galaxy_clusters/index", data={"galaxy_id": 1}
            )


class TestShowCluster:
    """Tests for show_cluster command."""

    def test_show_cluster_json_output(self):
        """Test showing a cluster with JSON output."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "GalaxyCluster": {"id": 1, "name": "Test Cluster", "description": "Test"}
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            show_cluster(cluster_id=1, json_output=True)

            mock_client.get_sync.assert_called_once_with("/galaxy_clusters/view/1")


class TestSearchGalaxies:
    """Tests for search_galaxies command."""

    def test_search_galaxies_basic(self):
        """Test searching galaxies uses POST with searchall."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {
            "galaxies": [{"id": 1, "name": "ransomware"}]
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            search_galaxies(
                term="ransomware",
                json_output=True, table_output=False, csv_output=False
            )

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert call_args[0][0] == "/galaxies/index"
            assert call_args[1]["data"]["searchall"] == "ransomware"


class TestAttachCluster:
    """Tests for attach_cluster command."""

    def test_attach_cluster_to_event(self):
        """Test attaching a galaxy cluster to an event."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "Cluster attached"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            attach_cluster(
                event_id=1,
                cluster_id=2,
                json_output=True
            )

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert "/events/attachCluster/1" in call_args[0][0]
            assert call_args[1]["data"]["GalaxyCluster"]["id"] == 2


class TestDetachCluster:
    """Tests for detach_cluster command."""

    def test_detach_cluster_from_event(self):
        """Test detaching a galaxy cluster from an event."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "Cluster detached"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            detach_cluster(
                event_id=1,
                cluster_id=2,
                json_output=True
            )

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert "/events/detachCluster/1" in call_args[0][0]


class TestListEventGalaxies:
    """Tests for list_event_galaxies command."""

    def test_list_event_galaxies_json_output(self):
        """Test listing galaxies attached to an event."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "Event": {
                "id": 1,
                "info": "Test Event",
                "Galaxy": [
                    {"id": 1, "name": "ransomware"},
                    {"id": 2, "name": "malware"}
                ]
            }
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_event_galaxies(
                event_id=1, json_output=True, table_output=False, csv_output=False
            )

            mock_client.get_sync.assert_called_once_with("/events/view/1", params={"galaxy": 1})
