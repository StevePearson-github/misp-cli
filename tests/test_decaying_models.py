"""Tests for decaying model commands."""

import json
from unittest.mock import MagicMock, patch

import pytest

from misp_cli.cli.commands.decaying_models import (
    list_decaying_models,
    show_decaying_model,
    enable_decaying_model,
    disable_decaying_model,
    import_decaying_model,
    export_decaying_model,
    delete_decaying_model,
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


class TestListDecayingModels:
    """Tests for list_decaying_models command."""

    def test_list_decaying_models_json_output(self):
        """Test listing decaying models with JSON output."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "DecayingModel": [
                {"id": 1, "name": "Model 1"},
                {"id": 2, "name": "Model 2"}
            ]
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_decaying_models(
                limit=50, page=1,
                json_output=True, table_output=False, csv_output=False
            )

            mock_client.get_sync.assert_called_once()
            call_args = mock_client.get_sync.call_args
            assert call_args[0][0] == "/decayingModel/index.json"

    def test_list_decaying_models_with_limit(self):
        """Test listing decaying models with custom limit."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {"DecayingModel": []}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_decaying_models(
                limit=100, page=1,
                json_output=True, table_output=False, csv_output=False
            )

            call_args = mock_client.get_sync.call_args
            assert call_args[1]["params"]["limit"] == 100

    def test_list_decaying_models_with_page(self):
        """Test listing decaying models with page."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {"DecayingModel": []}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            list_decaying_models(
                limit=50, page=2,
                json_output=True, table_output=False, csv_output=False
            )

            call_args = mock_client.get_sync.call_args
            assert call_args[1]["params"]["page"] == 2


class TestShowDecayingModel:
    """Tests for show_decaying_model command."""

    def test_show_decaying_model_json_output(self):
        """Test showing a decaying model with JSON output."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "DecayingModel": {"id": 1, "name": "Test Model"}
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            show_decaying_model(model_id=1, json_output=True)

            mock_client.get_sync.assert_called_once_with("/decayingModels/view/1")


class TestEnableDecayingModel:
    """Tests for enable_decaying_model command."""

    def test_enable_decaying_model(self):
        """Test enabling a decaying model."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "Model enabled"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            enable_decaying_model(model_id=1, json_output=True)

            mock_client.post_sync.assert_called_once_with("/decayingModels/enable/1")


class TestDisableDecayingModel:
    """Tests for disable_decaying_model command."""

    def test_disable_decaying_model(self):
        """Test disabling a decaying model."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "Model disabled"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            disable_decaying_model(model_id=1, json_output=True)

            mock_client.post_sync.assert_called_once_with("/decayingModels/disable/1")


class TestImportDecayingModel:
    """Tests for import_decaying_model command."""

    def test_import_decaying_model_success(self):
        """Test importing a decaying model from JSON file."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {
            "DecayingModel": {"id": 42, "name": "Imported Model"}
        }

        # Create a temporary JSON file
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"name": "Test Model", "description": "Test"}, f)
            temp_file = f.name

        try:
            with patch("misp_cli.cli.app.get_app", return_value=mock_app):
                import_decaying_model(model_file=temp_file, json_output=True)

                mock_client.post_sync.assert_called_once()
                call_args = mock_client.post_sync.call_args
                assert "/decayingModels/import" in call_args[0][0]
        finally:
            os.unlink(temp_file)

    def test_import_decaying_model_file_not_found(self):
        """Test importing from non-existent file."""
        mock_app, mock_config, mock_client = setup_mock_app()

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            from click.exceptions import Exit as ClickExit
            with pytest.raises((SystemExit, ClickExit)):
                import_decaying_model(model_file="/nonexistent/file.json", json_output=True)

    def test_import_decaying_model_invalid_json(self):
        """Test importing from invalid JSON file."""
        mock_app, mock_config, mock_client = setup_mock_app()

        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("not valid json")
            temp_file = f.name

        try:
            with patch("misp_cli.cli.app.get_app", return_value=mock_app):
                from click.exceptions import Exit as ClickExit
                with pytest.raises((SystemExit, ClickExit)):
                    import_decaying_model(model_file=temp_file, json_output=True)
        finally:
            os.unlink(temp_file)


class TestExportDecayingModel:
    """Tests for export_decaying_model command."""

    def test_export_decaying_model_json_output(self):
        """Test exporting a decaying model with JSON output."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "DecayingModel": {"id": 1, "name": "Test Model"}
        }

        mock_app.console = MagicMock()

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            export_decaying_model(model_id=1, output_file=None, json_output=True)

            mock_client.get_sync.assert_called_once_with("/decayingModels/export/1")


class TestListDecayingModelsCount:
    """Tests for list_decaying_models --count."""

    def test_list_decaying_models_count(self):
        """Test that --count returns count and exits without limit in request."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.get_sync.return_value = {
            "DecayingModel": [{"id": 1, "name": "Model 1"}, {"id": 2, "name": "Model 2"}]
        }

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            with pytest.raises(Exception):
                list_decaying_models(
                    limit=50, page=1,
                    json_output=True, table_output=False, csv_output=False,
                    count=True
                )

        call_args = mock_client.get_sync.call_args
        assert "limit" not in call_args[1]["params"]


class TestDeleteDecayingModel:
    """Tests for delete_decaying_model command."""

    def test_delete_decaying_model_with_force(self):
        """Test deleting a decaying model with force flag."""
        mock_app, mock_config, mock_client = setup_mock_app()
        mock_client.post_sync.return_value = {"message": "Model deleted"}

        with patch("misp_cli.cli.app.get_app", return_value=mock_app):
            delete_decaying_model(model_id=1, force=True, json_output=True)

            mock_client.post_sync.assert_called_once_with("/decayingModels/delete/1")
