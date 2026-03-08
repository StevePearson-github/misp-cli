"""Tests for MISP CLI exceptions."""

import pytest

from misp_cli.core.exceptions import (
    MISPError,
    MISPConfigurationError,
    MISPAPIError,
    MISPConnectionError,
    MISPAuthenticationError,
    MISPValidationError,
    MISPNotFoundError,
    MISPRateLimitError,
    MISPOutputError,
)


class TestMISPError:
    """Tests for base MISPError exception."""

    def test_basic_error(self):
        """Test creating a basic MISPError."""
        error = MISPError("Test error message")
        assert str(error) == "Test error message"
        assert error.exit_code == 1
        assert error.details == {}

    def test_error_with_exit_code(self):
        """Test MISPError with custom exit code."""
        error = MISPError("Test error", exit_code=10)
        assert error.exit_code == 10

    def test_error_with_details(self):
        """Test MISPError with details dictionary."""
        details = {"key": "value", "count": 5}
        error = MISPError("Test error", details=details)
        assert error.details == details


class TestMISPConfigurationError:
    """Tests for MISPConfigurationError."""

    def test_configuration_error_exit_code(self):
        """Test that configuration error has exit code 2."""
        error = MISPConfigurationError("Config error")
        assert error.exit_code == 2

    def test_configuration_error_with_details(self):
        """Test configuration error with details."""
        details = {"config_file": "/path/to/config"}
        error = MISPConfigurationError("Config error", details=details)
        assert error.details == details


class TestMISPAPIError:
    """Tests for MISPAPIError."""

    def test_api_error_basic(self):
        """Test basic API error."""
        error = MISPAPIError("API failed", status_code=500)
        assert error.status_code == 500
        assert error.exit_code == 3

    def test_api_error_with_response_body(self):
        """Test API error with response body."""
        error = MISPAPIError("API failed", status_code=400, response_body='{"error": "bad request"}')
        assert error.response_body == '{"error": "bad request"}'

    def test_api_error_str_includes_error_type(self):
        """Test that __str__ includes error type."""
        error = MISPAPIError("API failed", status_code=404, error_type="Not Found")
        assert "Not Found" in str(error)
        assert "API failed" in str(error)


class TestMISPConnectionError:
    """Tests for MISPConnectionError."""

    def test_connection_error_exit_code(self):
        """Test that connection error has exit code 4."""
        error = MISPConnectionError("Connection refused")
        assert error.exit_code == 4


class TestMISPAuthenticationError:
    """Tests for MISPAuthenticationError."""

    def test_authentication_error_exit_code(self):
        """Test that auth error has exit code 5."""
        error = MISPAuthenticationError("Auth failed")
        assert error.exit_code == 5

    def test_authentication_error_default_status(self):
        """Test that auth error defaults to 401."""
        error = MISPAuthenticationError("Auth failed")
        assert error.status_code == 401

    def test_permission_error_suggestion(self):
        """Test that permission errors include suggestions."""
        error = MISPAuthenticationError("Permission denied")
        error_str = str(error)
        assert "Suggestion:" in error_str

    def test_access_denied_suggestion(self):
        """Test that access denied errors include suggestions."""
        error = MISPAuthenticationError("Access denied")
        error_str = str(error)
        assert "Suggestion:" in error_str

    def test_readonly_error_suggestion(self):
        """Test that readonly errors include suggestions."""
        error = MISPAuthenticationError("System is in readonly mode")
        error_str = str(error)
        assert "Suggestion:" in error_str

    def test_non_permission_error_no_suggestion(self):
        """Test that regular errors don't include suggestions."""
        error = MISPAuthenticationError("Invalid credentials")
        error_str = str(error)
        assert "Suggestion:" not in error_str


class TestMISPValidationError:
    """Tests for MISPValidationError."""

    def test_validation_error_exit_code(self):
        """Test that validation error has exit code 6."""
        error = MISPValidationError("Invalid input")
        assert error.exit_code == 6


class TestMISPNotFoundError:
    """Tests for MISPNotFoundError."""

    def test_not_found_error_exit_code(self):
        """Test that not found error has exit code 7."""
        error = MISPNotFoundError("Event", "123")
        assert error.exit_code == 7

    def test_not_found_error_message_format(self):
        """Test that not found error message has correct format."""
        error = MISPNotFoundError("Event", "123")
        assert "Event" in str(error)
        assert "123" in str(error)

    def test_not_found_error_status_code(self):
        """Test that not found error has 404 status."""
        error = MISPNotFoundError("Tag", "456")
        assert error.status_code == 404

    def test_not_found_error_attributes(self):
        """Test that not found error stores resource info."""
        error = MISPNotFoundError("Attribute", "789")
        assert error.resource_type == "Attribute"
        assert error.resource_id == "789"


class TestMISPRateLimitError:
    """Tests for MISPRateLimitError."""

    def test_rate_limit_error_exit_code(self):
        """Test that rate limit error has exit code 8."""
        error = MISPRateLimitError()
        assert error.exit_code == 8

    def test_rate_limit_error_default_retry(self):
        """Test default retry after value."""
        error = MISPRateLimitError()
        assert error.retry_after == 60

    def test_rate_limit_error_custom_retry(self):
        """Test custom retry after value."""
        error = MISPRateLimitError(retry_after=120)
        assert error.retry_after == 120

    def test_rate_limit_error_str_includes_retry(self):
        """Test that __str__ includes retry info."""
        error = MISPRateLimitError(retry_after=30)
        assert "30s" in str(error)


class TestMISPOutputError:
    """Tests for MISPOutputError."""

    def test_output_error_exit_code(self):
        """Test that output error has exit code 9."""
        error = MISPOutputError("Output error")
        assert error.exit_code == 9


class TestExceptionHierarchy:
    """Tests for exception class hierarchy."""

    def test_all_exceptions_inherit_from_misp_error(self):
        """Test that all custom exceptions inherit from MISPError."""
        exceptions = [
            MISPConfigurationError("test"),
            MISPAPIError("test", status_code=500),
            MISPConnectionError("test"),
            MISPAuthenticationError("test"),
            MISPValidationError("test"),
            MISPNotFoundError("test", "1"),
            MISPRateLimitError(),
            MISPOutputError("test"),
        ]
        for exc in exceptions:
            assert isinstance(exc, MISPError)

    def test_api_errors_inherit_from_misp_error(self):
        """Test that API-related errors inherit properly."""
        errors = [
            MISPAPIError("test", status_code=500),
            MISPAuthenticationError("test"),
            MISPNotFoundError("test", "1"),
            MISPRateLimitError(),
        ]
        for exc in errors:
            assert isinstance(exc, MISPAPIError)
