"""Pytest configuration and fixtures for MISP CLI tests."""

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator, Optional

import pytest
from pydantic import BaseModel


class TestConfig(BaseModel):
    """Test configuration model."""
    url: str = "https://misp.example.com"
    api_key: str = "test-api-key"
    verify_ssl: bool = True
    timeout: int = 30
    output_format: str = "json"


@pytest.fixture
def sample_config_content() -> str:
    """Sample configuration file content."""
    return '''; MISP CLI Configuration File
; Supports multiple MISP instance profiles

[DEFAULT]
; Default profile settings (applies to all profiles)
verify_ssl = true
timeout = 30
output_format = json
colorize = true

[profile:default]
; Default profile
url = https://misp.example.com
api_key = test-api-key
verify_ssl = true
timeout = 30
output_format = json
colorize = true

[profile:production]
; Production MISP instance
url = https://misp.production.example.com
api_key = prod-api-key
verify_ssl = true
timeout = 60
output_format = table
colorize = true

[profile:staging]
; Staging MISP instance
url = https://misp.staging.example.com
api_key = staging-api-key
verify_ssl = false
timeout = 30
output_format = json
colorize = true
'''


@pytest.fixture
def temp_config_file(sample_config_content: str) -> Generator[Path, None, None]:
    """Create a temporary configuration file."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".conf", delete=False
    ) as f:
        f.write(sample_config_content)
        config_path = Path(f.name)
    
    yield config_path
    
    # Cleanup
    if config_path.exists():
        os.unlink(config_path)


@pytest.fixture
def temp_config_dir(sample_config_content: str) -> Generator[Path, None, None]:
    """Create a temporary directory with configuration file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / ".misp-cli.conf"
        config_path.write_text(sample_config_content)
        yield config_path


@pytest.fixture
def mock_misp_response() -> Dict[str, Any]:
    """Mock MISP API response."""
    return {
        "name": "Success",
        "message": "Request processed successfully",
        "url": "/events/index",
        "events": [
            {
                "id": 1,
                "info": "Test Event 1",
                "date": "2024-01-15",
                "threat_level_id": 2,
                "analysis": 1,
                "distribution": 5,
                "org_id": 1,
                "org_name": "Test Org"
            },
            {
                "id": 2,
                "info": "Test Event 2",
                "date": "2024-01-16",
                "threat_level_id": 3,
                "analysis": 2,
                "distribution": 4,
                "org_id": 1,
                "org_name": "Test Org"
            }
        ]
    }


@pytest.fixture
def mock_event_response() -> Dict[str, Any]:
    """Mock single event response."""
    return {
        "Event": {
            "id": 1,
            "info": "Test Event",
            "date": "2024-01-15",
            "threat_level_id": 2,
            "analysis": 1,
            "distribution": 5,
            "org_id": 1,
            "org_name": "Test Org",
            "Attribute": [
                {
                    "id": 1,
                    "type": "ip-src",
                    "value": "192.168.1.1",
                    "category": "Network activity",
                    "comment": "Test comment"
                }
            ],
            "Tag": [
                {
                    "id": 1,
                    "name": "test-tag",
                    "color": "#0088cc"
                }
            ]
        }
    }


@pytest.fixture
def mock_user_response() -> Dict[str, Any]:
    """Mock user response."""
    return {
        "User": {
            "id": 1,
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "role_id": 1,
            "org_id": 1,
            "authkey": "test-auth-key"
        }
    }


@pytest.fixture
def mock_tag_response() -> Dict[str, Any]:
    """Mock tag response."""
    return {
        "Tag": {
            "id": 1,
            "name": "test-tag",
            "color": "#0088cc",
            "exportable": True,
            "hide_tag": False
        }
    }


@pytest.fixture
def mock_error_response() -> Dict[str, Any]:
    """Mock error response."""
    return {
        "name": "Not Found",
        "message": "Event not found",
        "url": "/events/view/999"
    }


@pytest.fixture
def env_overrides() -> Generator[None, None, None]:
    """Provide environment variable overrides."""
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ["MISP_CLI_URL"] = "https://test.misp.local"
    os.environ["MISP_CLI_API_KEY"] = "test-api-key"
    os.environ["MISP_CLI_VERIFY_SSL"] = "false"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing."""
    from click.testing import CliRunner
    from misp_cli.cli.app import app
    
    return CliRunner(app)
