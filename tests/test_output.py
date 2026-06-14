"""Tests for output utilities."""

import json
from unittest.mock import MagicMock, patch

import pytest

from misp_cli.cli.output import get_output_format, print_count, print_csv, print_json, print_table, unwrap_nested_data


class TestPrintCount:
    """Tests for print_count function."""

    def test_plain_text_output(self, capsys):
        items = [{"id": 1}, {"id": 2}]
        with pytest.raises(Exception):
            print_count(items, json_output=False, output_format="table")
        assert capsys.readouterr().out.strip() == "2"

    def test_json_output_via_flag(self, capsys):
        items = [{"id": 1}]
        with pytest.raises(Exception):
            print_count(items, json_output=True, output_format="table")
        assert json.loads(capsys.readouterr().out) == {"count": 1}

    def test_json_output_via_format(self, capsys):
        items = []
        with pytest.raises(Exception):
            print_count(items, json_output=False, output_format="json")
        assert json.loads(capsys.readouterr().out) == {"count": 0}

    def test_raises_system_exit(self):
        with pytest.raises(Exception):
            print_count([], json_output=False, output_format="table")


class TestGetOutputFormat:
    """Tests for get_output_format function."""

    def test_csv_output_takes_priority(self):
        """Test that CSV output takes priority over other formats."""
        mock_config = MagicMock()
        mock_config.output_format = "json"

        result = get_output_format(mock_config, json_output=False, table_output=False, csv_output=True)
        assert result == "csv"

    def test_table_output_takes_priority_over_json(self):
        """Test that table output takes priority over JSON."""
        mock_config = MagicMock()
        mock_config.output_format = "json"

        result = get_output_format(mock_config, json_output=False, table_output=True, csv_output=False)
        assert result == "table"

    def test_json_output_uses_option(self):
        """Test that JSON output option is respected."""
        mock_config = MagicMock()
        mock_config.output_format = "table"

        result = get_output_format(mock_config, json_output=True, table_output=False, csv_output=False)
        assert result == "json"

    def test_defaults_to_config_format(self):
        """Test that it defaults to config output format when no options set."""
        mock_config = MagicMock()
        mock_config.output_format = "csv"

        result = get_output_format(mock_config, json_output=False, table_output=False, csv_output=False)
        assert result == "csv"


class TestUnwrapNestedData:
    """Tests for unwrap_nested_data function."""

    def test_unwrap_list_with_key(self):
        """Test unwrapping a list of dicts with the specified key."""
        response = [
            {"Tag": {"id": 1, "name": "tag1"}},
            {"Tag": {"id": 2, "name": "tag2"}}
        ]
        result = unwrap_nested_data(response, "Tag")
        assert result == [{"id": 1, "name": "tag1"}, {"id": 2, "name": "tag2"}]

    def test_unwrap_dict_with_data_key(self):
        """Test unwrapping a dict with data key."""
        response = {
            "data": [
                {"Event": {"id": 1, "info": "Test"}},
                {"Event": {"id": 2, "info": "Test2"}}
            ]
        }
        result = unwrap_nested_data(response, "Event")
        assert result == [{"id": 1, "info": "Test"}, {"id": 2, "info": "Test2"}]

    def test_unwrap_dict_with_nested_key(self):
        """Test unwrapping a dict that has the key nested inside."""
        response = {"Event": {"id": 1, "info": "Test"}}
        result = unwrap_nested_data(response, "Event")
        assert result == [{"id": 1, "info": "Test"}]

    def test_unwrap_empty_response(self):
        """Test unwrapping an empty response."""
        response = {}
        result = unwrap_nested_data(response, "Event")
        assert result == []

    def test_unwrap_response_with_empty_data(self):
        """Test unwrapping response with empty data key."""
        response = {"data": []}
        result = unwrap_nested_data(response, "Event")
        assert result == []

    def test_unwrap_no_nesting(self):
        """Test unwrapping when data is not nested."""
        response = [{"id": 1, "name": "tag1"}, {"id": 2, "name": "tag2"}]
        result = unwrap_nested_data(response, "Tag")
        # Should return the original list when items don't have the key
        assert result == [{"id": 1, "name": "tag1"}, {"id": 2, "name": "tag2"}]


class TestPrintJson:
    """Tests for print_json function."""

    def test_print_json_with_dict(self, capsys):
        """Test printing a dictionary as JSON."""
        data = {"key": "value", "number": 42}

        print_json(data)

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed == data

    def test_print_json_with_list(self, capsys):
        """Test printing a list as JSON."""
        data = [{"id": 1}, {"id": 2}]

        print_json(data)

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed == data

    def test_print_json_handles_non_serializable(self, capsys):
        """Test that print_json handles non-serializable objects with default handler."""
        class CustomObject:
            def __str__(self):
                return "custom"

        data = {"obj": CustomObject()}

        print_json(data)

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["obj"] == "custom"


class TestPrintCsv:
    """Tests for print_csv function."""

    def test_print_csv_calls_format_as_csv(self):
        """Test that print_csv calls format_as_csv."""
        data = [
            {"id": 1, "name": "tag1"},
            {"id": 2, "name": "tag2"}
        ]

        # Directly test the function by patching at the right location
        with patch("misp_cli.core.client.MISPCLient.format_as_csv") as mock_csv:
            mock_csv.return_value = "id,name\n1,tag1\n2,tag2"
            from misp_cli.cli.output import print_csv
            print_csv(data)
            mock_csv.assert_called_once_with(data, None)


class TestPrintTable:
    """Tests for print_table function."""

    def test_print_table_empty_data(self, capsys):
        """Test printing table with empty data."""
        mock_console = MagicMock()

        with patch("misp_cli.cli.app.get_app") as mock_get_app:
            mock_app = MagicMock()
            mock_app.console = mock_console
            mock_get_app.return_value = mock_app

            print_table([])

            captured = capsys.readouterr()
            assert "No data available" in captured.out

    def test_print_table_with_data(self):
        """Test printing table with data."""
        mock_console = MagicMock()
        data = [{"id": 1, "name": "tag1"}]

        with patch("misp_cli.cli.app.get_app") as mock_get_app:
            mock_app = MagicMock()
            mock_app.console = mock_console
            mock_get_app.return_value = mock_app

            with patch("misp_cli.core.client.MISPCLient.flatten_dict") as mock_flatten:
                mock_flatten.return_value = {"id": "1", "name": "tag1"}

                print_table(data)

                mock_console.print.assert_called_once()
