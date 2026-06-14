"""Configuration management for MISP CLI."""

import configparser
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class MISPProfile(BaseModel):
    """Configuration for a single MISP profile."""

    url: str = Field(..., description="Base URL of MISP instance")
    api_key: str = Field(..., description="MISP API authentication key")
    verify_ssl: bool = Field(default=True, description="Enable SSL verification")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")
    output_format: str = Field(default="json", description="Default output format")
    colorize: bool = Field(default=True, description="Enable colored output")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v.rstrip("/")

    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        """Validate output format."""
        valid_formats = ("json", "table", "csv")
        if v not in valid_formats:
            raise ValueError(f"Invalid output format: {v}. Must be one of {valid_formats}")
        return v


class CLIConfig(BaseModel):
    """Main configuration model."""

    default_profile: str = Field(default="default", description="Default profile name")
    profiles: dict[str, MISPProfile] = Field(default_factory=dict, description="MISP profiles")

    def get_profile(self, name: str | None = None) -> MISPProfile:
        """Get a profile by name or the default profile."""
        profile_name = name or self.default_profile
        if profile_name in self.profiles:
            return self.profiles[profile_name]
        raise ValueError(f"Profile '{profile_name}' not found in configuration")


class ConfigManager:
    """Manages configuration loading and validation."""

    def __init__(self, config_path: Path | None = None):
        """Initialize the configuration manager.

        Args:
            config_path: Optional path to config file. If not provided,
                        will search for config in standard locations.
        """
        self.config_path = config_path or self._find_config()
        self.config: CLIConfig | None = None

    def _find_config(self) -> Path | None:
        """Find the configuration file in standard locations.

        Search order:
        1. MISP_CLI_CONFIG environment variable
        2. ~/.misp-cli.conf (user home directory)
        3. ./.misp-cli.conf (current working directory)
        """
        # Check environment variable
        env_path = os.environ.get("MISP_CLI_CONFIG")
        if env_path:
            path = Path(env_path)
            if path.exists():
                return path

        # Check user home directory
        home_config = Path.home() / ".misp-cli.conf"
        if home_config.exists():
            return home_config

        # Check current directory
        cwd_config = Path.cwd() / ".misp-cli.conf"
        if cwd_config.exists():
            return cwd_config

        return None

    def _parse_bool(self, value: str) -> bool:
        """Parse boolean value from string."""
        return value.lower() in ("true", "1", "yes", "on")

    def _parse_config(self, config_path: Path) -> dict[str, Any]:
        """Parse INI configuration file."""
        parser = configparser.ConfigParser()
        parser.read(config_path)

        config_data: dict[str, Any] = {"default_profile": "default", "profiles": {}}

        # Parse DEFAULT section first
        if "DEFAULT" in parser:
            default_section = dict(parser["DEFAULT"])
            if "default_profile" in default_section:
                config_data["default_profile"] = default_section["default_profile"].strip()

        # Parse profile sections
        for section in parser.sections():
            if section.startswith("profile:"):
                profile_name = section.split(":", 1)[1].strip()
                profile_data: dict[str, Any] = {}

                section_dict = dict(parser[section])

                # Get values from section or DEFAULT
                profile_data["url"] = section_dict.get("url", "").strip()
                profile_data["api_key"] = section_dict.get("api_key", "").strip()

                # Boolean values
                profile_data["verify_ssl"] = self._parse_bool(
                    section_dict.get("verify_ssl", "true")
                )
                profile_data["colorize"] = self._parse_bool(section_dict.get("colorize", "true"))

                # Integer values
                try:
                    profile_data["timeout"] = int(section_dict.get("timeout", "30"))
                except ValueError:
                    profile_data["timeout"] = 30

                # String values
                profile_data["output_format"] = section_dict.get("output_format", "json").strip()

                config_data["profiles"][profile_name] = profile_data

        # Check for legacy [default] section (without profile: prefix)
        if "default" in parser and not any(s.startswith("profile:") for s in parser.sections()):
            section_dict = dict(parser["default"])
            config_data["profiles"]["default"] = {
                "url": section_dict.get("url", "").strip(),
                "api_key": section_dict.get("api_key", "").strip(),
                "verify_ssl": self._parse_bool(section_dict.get("verify_ssl", "true")),
                "timeout": int(section_dict.get("timeout", "30")),
                "output_format": section_dict.get("output_format", "json"),
                "colorize": self._parse_bool(section_dict.get("colorize", "true")),
            }

        return config_data

    def _apply_env_overrides(self, config_data: dict[str, Any]) -> dict[str, Any]:
        """Apply environment variable overrides to configuration."""
        # Environment variables override config file
        env_url = os.environ.get("MISP_CLI_URL")
        env_api_key = os.environ.get("MISP_CLI_API_KEY")
        env_verify_ssl = os.environ.get("MISP_CLI_VERIFY_SSL")
        env_timeout = os.environ.get("MISP_CLI_TIMEOUT")
        env_output = os.environ.get("MISP_CLI_OUTPUT_FORMAT")
        env_profile = os.environ.get("MISP_CLI_PROFILE")

        if env_profile:
            config_data["default_profile"] = env_profile

        # Apply to default profile
        if "default" in config_data["profiles"] or not config_data["profiles"]:
            profile_key = config_data["default_profile"] or "default"
            if profile_key in config_data["profiles"]:
                profile = config_data["profiles"][profile_key]
                if env_url:
                    profile["url"] = env_url
                if env_api_key:
                    profile["api_key"] = env_api_key
                if env_verify_ssl:
                    profile["verify_ssl"] = self._parse_bool(env_verify_ssl)
                if env_timeout:
                    try:
                        profile["timeout"] = int(env_timeout)
                    except ValueError:
                        pass
                if env_output:
                    profile["output_format"] = env_output

        return config_data

    def load(self) -> CLIConfig:
        """Load configuration from file.

        Returns:
            CLIConfig object with loaded configuration.

        Raises:
            FileNotFoundError: If config file not found.
            ValueError: If configuration is invalid.
        """
        if self.config_path is None or not self.config_path.exists():
            raise FileNotFoundError(
                "Configuration file not found. Searched in: "
                "MISP_CLI_CONFIG, ~/.misp-cli.conf, ./.misp-cli.conf"
            )

        config_data = self._parse_config(self.config_path)
        config_data = self._apply_env_overrides(config_data)

        # Set default profile if not specified
        if not config_data.get("default_profile"):
            config_data["default_profile"] = "default"

        # Ensure at least a default profile exists
        if not config_data.get("profiles"):
            config_data["profiles"]["default"] = {}

        self.config = CLIConfig(**config_data)
        return self.config

    def validate(self) -> bool:
        """Validate the current configuration.

        Returns:
            True if configuration is valid.

        Raises:
            ValueError: If configuration is invalid.
        """
        config = self.load()

        # Validate each profile
        for name, profile in config.profiles.items():
            if not profile.url:
                raise ValueError(f"Profile '{name}': URL is required")
            if not profile.api_key:
                raise ValueError(f"Profile '{name}': API key is required")

        return True

    def create_default_config(self, path: Path | None = None) -> Path:
        """Create a default configuration file.

        Args:
            path: Path to create the config file. If not provided,
                  will create in the current working directory.

        Returns:
            Path to the created configuration file.
        """
        config_path = path or Path.cwd() / ".misp-cli.conf"

        config_content = """; MISP CLI Configuration File
; Supports multiple MISP instance profiles

[DEFAULT]
; Default profile settings (applies to all profiles)
default_profile = default
verify_ssl = true
timeout = 30
output_format = json
colorize = true

[profile:default]
; Default profile
url = https://misp.example.com
api_key = your-api-key-here
verify_ssl = true
timeout = 30
output_format = json
colorize = true

[profile:production]
; Production MISP instance
url = https://misp.production.example.com
api_key = your-production-api-key
verify_ssl = true
timeout = 60
output_format = table
colorize = true

[profile:staging]
; Staging MISP instance
url = https://misp.staging.example.com
api_key = your-staging-api-key
verify_ssl = false
timeout = 30
output_format = json
colorize = true

[profile:sandbox]
; Local development/sandbox
url = http://localhost:5000
api_key = your-sandbox-api-key
verify_ssl = false
timeout = 15
output_format = json
colorize = false
"""

        config_path.write_text(config_content)
        return config_path

    def set_default_profile(self, profile_name: str) -> None:
        """Set the default profile in the configuration file.

        Args:
            profile_name: Name of the profile to set as default.

        Raises:
            FileNotFoundError: If config file not found.
            ValueError: If profile doesn't exist.
        """
        if self.config_path is None or not self.config_path.exists():
            raise FileNotFoundError(
                "Configuration file not found. Searched in: "
                "MISP_CLI_CONFIG, ~/.misp-cli.conf, ./.misp-cli.conf"
            )

        # Load config to verify profile exists
        config = self.load()
        if profile_name not in config.profiles:
            available = ", ".join(config.profiles.keys())
            raise ValueError(f"Profile '{profile_name}' not found. Available profiles: {available}")

        # Read the config file and modify default_profile
        parser = configparser.ConfigParser()
        parser.read(self.config_path)

        # Ensure DEFAULT section exists
        if "DEFAULT" not in parser:
            parser.add_section("DEFAULT")

        # Set the default profile
        parser.set("DEFAULT", "default_profile", profile_name)

        # Write back to file
        with open(self.config_path, "w") as f:
            parser.write(f)


class MISPConfig:
    """Convenience class for loading MISP configuration.

    This class provides a simple interface for loading configuration
    from a file and accessing the active profile.
    """

    def __init__(
        self,
        url: str,
        api_key: str,
        verify_ssl: bool = True,
        timeout: int = 30,
        output_format: str = "json",
    ):
        """Initialize MISPConfig with values.

        Args:
            url: MISP instance URL
            api_key: MISP API key
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds
            output_format: Default output format
        """
        self.url = url
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.output_format = output_format

    @classmethod
    def from_file(cls, config_path: Path | None = None) -> "MISPConfig":
        """Load configuration from file.

        Args:
            config_path: Optional path to config file. If not provided,
                       will search for config in standard locations.

        Returns:
            MISPConfig instance with loaded configuration.

        Raises:
            FileNotFoundError: If config file not found.
        """
        manager = ConfigManager(config_path)
        config = manager.load()
        profile = config.get_profile()

        return cls(
            url=profile.url,
            api_key=profile.api_key,
            verify_ssl=profile.verify_ssl,
            timeout=profile.timeout,
            output_format=profile.output_format,
        )
