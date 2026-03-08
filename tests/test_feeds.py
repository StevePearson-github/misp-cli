"""Tests for feed commands."""

from unittest.mock import MagicMock, patch

import pytest

from misp_cli.cli.commands.feeds import (
    list_feeds,
    show_feed,
    create_feed,
    edit_feed,
    delete_feed,
    fetch_feed,
    cache_feed,
    enable_feed,
    disable_feed,
    import_feed,
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


class TestListFeeds:
    """Tests for list_feeds command."""

    def test_list_feeds_json_output(self):
        """Test listing feeds with JSON output."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "feeds": [
                {"id": 1, "name": "Feed 1", "provider": "Provider A"},
                {"id": 2, "name": "Feed 2", "provider": "Provider B"}
            ]
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_feeds(
                limit=50, page=1, enabled_only=False,
                json_output=True, table_output=False, csv_output=False, quiet=False
            )

            mock_client.get_sync.assert_called_once()
            call_args = mock_client.get_sync.call_args
            assert call_args[0][0] == "/feeds/index"

    def test_list_feeds_with_limit(self):
        """Test listing feeds with custom limit."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {"feeds": []}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_feeds(
                limit=100, page=1, enabled_only=False,
                json_output=True, table_output=False, csv_output=False, quiet=False
            )

            call_args = mock_client.get_sync.call_args
            assert call_args[1]["params"]["limit"] == 100

    def test_list_feeds_enabled_only(self):
        """Test listing feeds with enabled_only filter."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {"feeds": []}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_feeds(
                limit=50, page=1, enabled_only=True,
                json_output=True, table_output=False, csv_output=False, quiet=False
            )

            call_args = mock_client.get_sync.call_args
            assert call_args[1]["params"]["enabled"] == 1

    def test_list_feeds_quiet_mode(self):
        """Test listing feeds with quiet mode."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {"feeds": [{"id": 1, "name": "Feed 1"}]}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_feeds(
                limit=50, page=1, enabled_only=False,
                json_output=True, table_output=False, csv_output=False, quiet=True
            )

            # Should not raise, quiet mode suppresses output

    def test_list_feeds_unwrap_nested(self):
        """Test that nested Feed structure is properly unwrapped."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "feeds": [
                {"Feed": {"id": 1, "name": "Feed 1"}},
                {"Feed": {"id": 2, "name": "Feed 2"}}
            ]
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_feeds(
                limit=50, page=1, enabled_only=False,
                json_output=True, table_output=False, csv_output=False, quiet=False
            )

            # Verify client was called
            mock_client.get_sync.assert_called_once()


class TestShowFeed:
    """Tests for show_feed command."""

    def test_show_feed_json_output(self):
        """Test showing a feed with JSON output."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "Feed": {"id": 1, "name": "Test Feed", "url": "https://example.com/feed"}
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            show_feed(feed_id=1, json_output=True)

            mock_client.get_sync.assert_called_once_with("/feeds/view/1")


class TestCreateFeed:
    """Tests for create_feed command."""

    def test_create_feed_basic(self):
        """Test creating a basic feed."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {
            "Feed": {"id": 42, "name": "New Feed"}
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            create_feed(
                name="New Feed",
                url="https://example.com/feed",
                provider="Test Provider",
                format_type="misp",
                enabled=False,
                json_output=True
            )

            mock_client.post_sync.assert_called_once()
            call_args = mock_client.post_sync.call_args
            assert "/feeds/add" in call_args[0][0]
            assert call_args[1]["data"]["Feed"]["name"] == "New Feed"
            assert call_args[1]["data"]["Feed"]["url"] == "https://example.com/feed"

    def test_create_feed_with_enabled(self):
        """Test creating a feed with enabled flag."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"Feed": {"id": 1}}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            create_feed(
                name="Enabled Feed",
                url="https://example.com/feed",
                provider="Test",
                format_type="misp",
                enabled=True,
                json_output=True
            )

            call_args = mock_client.post_sync.call_args
            assert call_args[1]["data"]["Feed"]["enabled"] is True


class TestEditFeed:
    """Tests for edit_feed command."""

    def test_edit_feed_name(self):
        """Test editing feed name."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "Feed updated"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            edit_feed(
                feed_id=1,
                name="Updated Name",
                url=None,
                provider=None,
                enabled=None,
                json_output=True
            )

            call_args = mock_client.post_sync.call_args
            assert "/feeds/edit/1" in call_args[0][0]
            assert call_args[1]["data"]["Feed"]["name"] == "Updated Name"

    def test_edit_feed_no_changes(self):
        """Test editing feed with no changes specified."""
        mock_app, mock_config, mock_client = setup_mock_app()

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            from click.exceptions import Exit as ClickExit
            with pytest.raises((SystemExit, ClickExit)):
                edit_feed(
                    feed_id=1,
                    name=None,
                    url=None,
                    provider=None,
                    enabled=None,
                    json_output=False
                )


class TestDeleteFeed:
    """Tests for delete_feed command."""

    def test_delete_feed_with_force(self):
        """Test deleting a feed with force flag."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "Feed deleted"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            delete_feed(feed_id=1, force=True, json_output=True)

            mock_client.post_sync.assert_called_once_with("/feeds/delete/1")


class TestFetchFeed:
    """Tests for fetch_feed command."""

    def test_fetch_feed(self):
        """Test fetching events from a feed."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {"message": "Fetched"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            fetch_feed(feed_id=1, json_output=True)

            mock_client.get_sync.assert_called_once_with("/feeds/fetch/1")


class TestCacheFeed:
    """Tests for cache_feed command."""

    def test_cache_feed(self):
        """Test caching a feed."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {"message": "Cached"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            cache_feed(feed_id=1, json_output=True)

            mock_client.get_sync.assert_called_once_with("/feeds/cache/1")


class TestEnableFeed:
    """Tests for enable_feed command."""

    def test_enable_feed(self):
        """Test enabling a feed."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "Enabled"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            enable_feed(feed_id=1, json_output=True)

            mock_client.post_sync.assert_called_once_with("/feeds/enable/1")


class TestDisableFeed:
    """Tests for disable_feed command."""

    def test_disable_feed(self):
        """Test disabling a feed."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "Disabled"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            disable_feed(feed_id=1, json_output=True)

            mock_client.post_sync.assert_called_once_with("/feeds/disable/1")


class TestImportFeed:
    """Tests for import_feed command."""

    def test_import_feed(self):
        """Test importing events from a feed."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {"message": "Imported"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            import_feed(feed_id=1, json_output=True)

            mock_client.get_sync.assert_called_once_with("/feeds/import/1")


