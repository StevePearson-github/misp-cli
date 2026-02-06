"""Tests for configuration management."""

import os
import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from misp_cli.core.config import ConfigManager, CLIConfig, MISPProfile


class TestMISPProfile:
    """Tests for MISPProfile model."""

    def test_valid_profile(self):
        """Test creating a valid profile."""
        profile = MISPProfile(
            url="https://misp.example.com",
            api_key="test-api-key",
            verify_ssl=True,
            timeout=30,
            output_format="json",
        )
        assert profile.url == "https://misp.example.com"
        assert profile.api_key == "test-api-key"
        assert profile.verify_ssl is True
        assert profile.timeout == 30
        assert profile.output_format == "json"

    def test_url_trailing_slash_removed(self):
        """Test that trailing slash is removed from URL."""
        profile = MISPProfile(
            url="https://misp.example.com/",
            api_key="test-api-key",
        )
        assert profile.url == "https://misp.example.com"

    def test_invalid_url_missing_protocol(self):
        """Test that invalid URL without protocol raises error."""
        with pytest.raises(ValidationError) as exc_info:
            MISPProfile(
                url="misp.example.com",
                api_key="test-api-key",
            )
        assert "http:// or https://" in str(exc_info.value)

    def test_invalid_output_format(self):
        """Test that invalid output format raises error."""
        with pytest.raises(ValidationError):
            MISPProfile(
                url="https://misp.example.com",
                api_key="test-api-key",
                output_format="invalid",
            )

    def test_timeout_bounds(self):
        """Test timeout value bounds."""
        # Valid bounds
        profile = MISPProfile(
            url="https://misp.example.com",
            api_key="test-api-key",
            timeout=1,
        )
        assert profile.timeout == 1
        
        profile = MISPProfile(
            url="https://misp.example.com",
            api_key="test-api-key",
            timeout=300,
        )
        assert profile.timeout == 300
        
        # Invalid bounds
        with pytest.raises(ValidationError):
            MISPProfile(
                url="https://misp.example.com",
                api_key="test-api-key",
                timeout=0,
            )
        
        with pytest.raises(ValidationError):
            MISPProfile(
                url="https://misp.example.com",
                api_key="test-api-key",
                timeout=301,
            )


class TestCLIConfig:
    """Tests for CLIConfig model."""

    def test_default_profile(self):
        """Test default profile name."""
        config = CLIConfig()
        assert config.default_profile == "default"

    def test_get_profile(self):
        """Test getting a profile."""
        config = CLIConfig(
            default_profile="production",
            profiles={
                "default": MISPProfile(
                    url="https://default.example.com",
                    api_key="default-key",
                ),
                "production": MISPProfile(
                    url="https://prod.example.com",
                    api_key="prod-key",
                ),
            },
        )
        
        # Get profile by name
        prod_profile = config.get_profile("production")
        assert prod_profile.url == "https://prod.example.com"

    def test_get_nonexistent_profile(self):
        """Test getting a nonexistent profile raises error."""
        config = CLIConfig(
            profiles={
                "default": MISPProfile(
                    url="https://default.example.com",
                    api_key="default-key",
                ),
            },
        )
        
        with pytest.raises(ValueError) as exc_info:
            config.get_profile("nonexistent")
        assert "not found in configuration" in str(exc_info.value)


class TestConfigManager:
    """Tests for ConfigManager class."""

    def test_parse_valid_config(self, temp_config_file: Path):
        """Test parsing a valid configuration file."""
        manager = ConfigManager(config_path=temp_config_file)
        config = manager.load()
        
        assert config.default_profile == "default"
        assert "default" in config.profiles
        assert "production" in config.profiles
        assert "staging" in config.profiles
        
        default_profile = config.profiles["default"]
        assert default_profile.url == "https://misp.example.com"
        assert default_profile.api_key == "test-api-key"
        assert default_profile.verify_ssl is True
        assert default_profile.timeout == 30
        assert default_profile.output_format == "json"

    def test_config_not_found(self):
        """Test error when config file not found."""
        manager = ConfigManager(config_path=Path("/nonexistent/config.conf"))
        
        with pytest.raises(FileNotFoundError):
            manager.load()

    def test_create_default_config(self):
        """Test creating a default configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".misp-cli.conf"
            
            manager = ConfigManager()
            created_path = manager.create_default_config(config_path)
            
            assert created_path.exists()
            content = created_path.read_text()
            assert "[profile:default]" in content
            assert "https://misp.example.com" in content

    def test_env_overrides(self, temp_config_file: Path, env_overrides):
        """Test environment variable overrides."""
        manager = ConfigManager(config_path=temp_config_file)
        config = manager.load()
        
        # Environment should override config file
        profile = config.get_profile()
        assert profile.url == "https://test.misp.local"
        assert profile.api_key == "test-api-key"
        assert profile.verify_ssl is False

    def test_profile_selection(self, temp_config_file: Path):
        """Test selecting a specific profile."""
        manager = ConfigManager(config_path=temp_config_file)
        config = manager.load()
        
        # Get production profile
        prod_profile = config.get_profile("production")
        assert prod_profile.url == "https://misp.production.example.com"
        assert prod_profile.output_format == "table"

    def test_staging_profile(self, temp_config_file: Path):
        """Test staging profile has correct settings."""
        manager = ConfigManager(config_path=temp_config_file)
        config = manager.load()
        
        staging = config.get_profile("staging")
        assert staging.verify_ssl is False
        assert staging.timeout == 30
