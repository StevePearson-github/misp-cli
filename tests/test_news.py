"""Tests for news commands."""

from unittest.mock import MagicMock, patch

import pytest
import typer

from misp_cli.cli.commands.news import list_news, show_news, create_news


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


SAMPLE_NEWS = [
    {"id": "1", "title": "First item", "message": "Hello"},
    {"id": "2", "title": "Second item", "message": "World"},
]


class TestListNews:
    def test_list_news_no_query_params(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = SAMPLE_NEWS

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_news(limit=50, json_output=True, table_output=False, csv_output=False)

        call_args = mock_client.get_sync.call_args
        assert call_args[0][0] == "/news/index"
        assert call_args[1] == {} or call_args[1].get("params") is None

    def test_list_news_applies_client_side_limit(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        many_items = [{"id": str(i), "title": f"Item {i}"} for i in range(10)]
        mock_client.get_sync.return_value = many_items

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_news(limit=3, json_output=True, table_output=False, csv_output=False)

        mock_client.get_sync.assert_called_once_with("/news/index")


class TestShowNews:
    def test_show_news_filters_by_id(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = SAMPLE_NEWS

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            show_news(news_id=2, json_output=True)

        mock_client.get_sync.assert_called_once_with("/news/index")

    def test_show_news_not_found_exits_with_error(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = SAMPLE_NEWS

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            with pytest.raises(typer.Exit) as exc_info:
                show_news(news_id=999, json_output=True)

        assert exc_info.value.exit_code == 1


class TestCreateNews:
    def test_create_news_wraps_in_news_key(self):
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"News": {"id": 5, "title": "My news"}}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            create_news(title="My news", message="Body text", json_output=True)

        call_args = mock_client.post_sync.call_args
        assert call_args[0][0] == "/news/add"
        body = call_args[1]["data"]
        assert "News" in body
        assert body["News"]["title"] == "My news"
