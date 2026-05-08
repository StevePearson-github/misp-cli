"""Tests for logs commands."""

from unittest.mock import MagicMock, patch

import pytest

from misp_cli.cli.commands.logs import search_logs, logs_by_date


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


class TestSearchLogs:
    def test_search_logs_uses_post_index(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = [{"Log": {"id": 1, "action": "login"}}]

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            search_logs(
                query="login",
                limit=100,
                json_output=True,
                table_output=False,
                csv_output=False,
                count=False,
            )

        mock_client.post_sync.assert_called_once()
        call_args = mock_client.post_sync.call_args
        assert "/logs/index" in call_args[0][0]
        assert call_args[1]["data"]["search"] == "login"

    def test_search_logs_passes_limit(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = []

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            search_logs(
                query="test",
                limit=25,
                json_output=True,
                table_output=False,
                csv_output=False,
                count=False,
            )

        body = mock_client.post_sync.call_args[1]["data"]
        assert body["limit"] == 25

    def test_search_logs_does_not_use_get(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = []

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            search_logs(
                query="login",
                limit=100,
                json_output=True,
                table_output=False,
                csv_output=False,
                count=False,
            )

        mock_client.get_sync.assert_not_called()


class TestLogsByDate:
    def test_date_logs_uses_post_index(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = []

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            logs_by_date(
                date_str="2026-05-07",
                limit=100,
                json_output=True,
                table_output=False,
                csv_output=False,
                count=False,
            )

        mock_client.post_sync.assert_called_once()
        call_args = mock_client.post_sync.call_args
        assert "/logs/index" in call_args[0][0]
        body = call_args[1]["data"]
        assert body["from"] == "2026-05-07"
        assert body["to"] == "2026-05-07"

    def test_date_logs_does_not_use_get(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = []

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            logs_by_date(
                date_str="2026-05-07",
                limit=100,
                json_output=True,
                table_output=False,
                csv_output=False,
                count=False,
            )

        mock_client.get_sync.assert_not_called()

    def test_date_logs_rejects_invalid_format(self):
        import typer

        mock_app, mock_config, mock_client = setup_mock_app()

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            with pytest.raises(typer.Exit):
                logs_by_date(
                    date_str="not-a-date",
                    limit=100,
                    json_output=True,
                    table_output=False,
                    csv_output=False,
                    count=False,
                )

        mock_client.post_sync.assert_not_called()
