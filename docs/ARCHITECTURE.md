# MISP CLI Architecture Document

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Project Structure](#2-project-structure)
3. [Configuration File Format](#3-configuration-file-format)
4. [CLI Command Hierarchy](#4-cli-command-hierarchy)
5. [Key Classes and Responsibilities](#5-key-classes-and-responsibilities)
6. [API Endpoint Mapping](#6-api-endpoint-mapping)
7. [Error Handling Strategy](#7-error-handling-strategy)
8. [Output Formatting](#8-output-formatting)
9. [Plugin Architecture](#9-plugin-architecture)
10. [Implementation Roadmap](#10-implementation-roadmap)

---

## 1. Project Overview

**Project Name**: misp-cli  
**Purpose**: Comprehensive command-line interface for interacting with MISP (Malware Information Sharing Platform)  
**Language**: Python 3.11+  
**Package Manager**: uv  
**CLI Framework**: Typer + Rich  
**Type System**: Fully typed with type hints

### 1.1 Goals

- Provide complete coverage of MISP OpenAPI endpoints
- Support multiple MISP instance configurations
- Modern CLI experience with Rich rendering
- Configurable output formats (JSON, Table, CSV, STIX)
- Extensible plugin architecture for custom endpoints

### 1.2 Technology Stack

```
Python 3.11+
├── typer              # CLI framework with auto-generated docs
├── rich               # Terminal output formatting
├── httpx              # Async HTTP client with OpenAPI support
├── pydantic           # Data validation and settings management
├── python-dotenv      # Environment variable support
└── stix2              # STIX/TAXII format support (optional)
```

---

## 2. Project Structure

```
misp-cli/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── misp_cli/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── app.py                 # Main Typer application
│       │   ├── options.py             # Global CLI options
│       │   ├── commands/              # Command modules
│       │   │   ├── __init__.py
│       │   │   ├── events.py
│       │   │   ├── attributes.py
│       │   │   ├── users.py
│       │   │   ├── organizations.py
│       │   │   ├── feeds.py
│       │   │   ├── servers.py
│       │   │   ├── galaxies.py
│       │   │   ├── warninglists.py
│       │   │   ├── noticelists.py
│       │   │   ├── tags.py
│       │   │   ├── roles.py
│       │   │   ├── shadow_attributes.py
│       │   │   └── audit_logs.py
│       │   └── formatters/            # Output formatters
│       │       ├── __init__.py
│       │       ├── json_formatter.py
│       │       ├── table_formatter.py
│       │       ├── csv_formatter.py
│       │       └── stix_formatter.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py              # Configuration management
│       │   ├── client.py              # HTTP client wrapper
│       │   ├── auth.py                # Authentication handler
│       │   ├── exceptions.py          # Custom exceptions
│       │   └── endpoints.py            # Endpoint registry
│       ├── models/
│       │   ├── __init__.py
│       │   ├── misp_models.py         # Pydantic models for MISP data
│       │   └── api_models.py          # API request/response models
│       ├── plugins/
│       │   ├── __init__.py
│       │   ├── base.py                # Plugin base class
│       │   └── registry.py            # Plugin registry
│       └── utils/
│           ├── __init__.py
│           ├── json_utils.py         # JSON utilities
│           └── validation.py         # Input validation
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_config.py
│   │   ├── test_client.py
│   │   └── test_commands/
│   └── integration/
│       ├── test_api_integration.py
│       └── test_e2e.py
├── docs/
│   ├── installation.md
│   ├── usage.md
│   ├── configuration.md
│   └── examples/
├── scripts/
│   ├── generate_openapi.py           # Generate endpoint mappings from OpenAPI
│   └── lint_check.sh
├── .misp-cli.conf                   # Example config file
├── .env.example                     # Environment template
└── .gitignore
```

---

## 3. Configuration File Format

### 3.1 Configuration File Location

The CLI will search for configuration files in the following order:

1. `--config` CLI parameter (highest priority)
2. `MISP_CLI_CONFIG` environment variable
3. `~/.misp-cli.conf` (user home directory)
4. `./.misp-cli.conf` (current working directory)

### 3.2 INI File Format Specification

```ini
; MISP CLI Configuration File
; Supports multiple MISP instance profiles

[DEFAULT]
; Default profile settings (applies to all profiles)
verify_ssl = true
timeout = 30
output_format = json
colorize = true

[profile:production]
; Production MISP instance
url = https://misp.example.com
api_key = your-production-api-key-here
verify_ssl = true
timeout = 60
output_format = table
colorize = true

[profile:staging]
; Staging/Development MISP instance
url = https://misp-staging.example.com
api_key = your-staging-api-key-here
verify_ssl = false
timeout = 30
output_format = json
colorize = true

[profile:sandbox]
; Sandboxed environment for testing
url = https://misp-sandbox.local
api_key = your-sandbox-api-key-here
verify_ssl = false
timeout = 15
output_format = json
colorize = false

[profile:taxii]
; TAXII-enabled MISP instance
url = https://taxii-misp.example.com
api_key = your-taxii-api-key-here
timeout = 30
output_format = stix
colorize = true
```

### 3.3 Configuration Schema

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| url | string | Yes | - | Base URL of MISP instance |
| api_key | string | Yes | - | MISP API authentication key |
| verify_ssl | boolean | No | `true` | Enable/disable SSL verification |
| timeout | integer | No | `30` | Request timeout in seconds |
| output_format | string | No | `json` | Default output format |
| colorize | boolean | No | `true` | Enable colored terminal output |

### 3.4 Environment Variables

The CLI supports environment variable overrides:

```bash
export MISP_CLI_URL="https://misp.example.com"
export MISP_CLI_API_KEY="your-api-key"
export MISP_CLI_VERIFY_SSL="true"
export MISP_CLI_TIMEOUT="30"
export MISP_CLI_OUTPUT_FORMAT="json"
export MISP_CLI_PROFILE="production"
```

### 3.5 Configuration Management

```python
# src/misp_cli/core/config.py

from pydantic import BaseModel, Field
from typing import Optional
from pathlib import Path

class MISPProfile(BaseModel):
    """Configuration for a single MISP profile."""
    url: str = Field(..., description="Base URL of MISP instance")
    api_key: str = Field(..., description="MISP API authentication key")
    verify_ssl: bool = Field(default=True, description="Enable SSL verification")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout")
    output_format: str = Field(default="json", description="Default output format")
    colorize: bool = Field(default=True, description="Enable colored output")

class CLIConfig(BaseModel):
    """Main configuration model."""
    default_profile: str = Field(default="default", description="Default profile name")
    profiles: dict[str, MISPProfile] = Field(default_factory=dict, description="MISP profiles")
    
    @property
    def active_profile(self) -> MISPProfile:
        """Get the active profile or default."""
        return self.profiles.get(self.default_profile, MISPProfile(
            url="http://localhost",
            api_key="",
            verify_ssl=False,
            timeout=30
        ))

class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self._find_config()
        self.config: Optional[CLIConfig] = None
    
    def load(self) -> CLIConfig:
        """Load configuration from file."""
        # Implementation details...
```

---

## 4. CLI Command Hierarchy

### 4.1 Global Options

```bash
misp-cli --help

# Global options:
#   --config FILE     Configuration file path
#   --profile TEXT    Profile name to use
#   --output FORMAT   Output format (json, table, csv, stix)
#   --no-color        Disable colored output
#   --verbose/-v      Enable verbose output
#   --debug           Enable debug mode
#   --version         Show version
#   --help            Show this message
```

### 4.2 Command Structure

```
misp-cli
├── events                      # Event management
│   ├── list                    # List events
│   │   ├── --page INT         # Page number
│   │   ├── --limit INT        # Items per page
│   │   ├── --search TEXT      # Search query
│   │   ├── --org TEXT         # Organization filter
│   │   └── --format FORMAT    # Output format
│   ├── show EVENT_ID          # Show event details
│   ├── create                 # Create new event
│   │   ├── --info TEXT        # Event info
│   │   ├── --threat-level INT # Threat level (1-4)
│   │   ├── --analysis INT     # Analysis level (0-2)
│   │   ├── --distribution INT # Distribution (0-5)
│   │   └── --date DATE        # Event date
│   ├── update EVENT_ID        # Update event
│   ├── delete EVENT_ID        # Delete event
│   ├── export EVENT_ID        # Export event
│   │   └── --format FORMAT    # Export format
│   ├── publish EVENT_ID       # Publish event
│   ├── unpublish EVENT_ID     # Unpublish event
│   └── sync                   # Sync events from/to MISP
│
├── attributes                  # Attribute management
│   ├── list EVENT_ID          # List attributes
│   ├── add EVENT_ID           # Add attribute
│   │   ├── --type TEXT        # Attribute type
│   │   ├── --value TEXT       # Attribute value
│   │   ├── --category TEXT    # Category
│   │   └── --comment TEXT     # Comment
│   ├── update ATTR_ID        # Update attribute
│   ├── delete ATTR_ID        # Delete attribute
│   └── search                 # Search attributes
│       ├── --type TEXT        # Attribute type
│       ├── --value TEXT       # Search value
│       └── --context           # Include context
│
├── users                       # User management
│   ├── list                    # List users
│   ├── show USER_ID            # Show user details
│   ├── create                  # Create user
│   ├── update USER_ID          # Update user
│   ├── delete USER_ID          # Delete user
│   └── current                 # Current user info
│
├── organizations              # Organization management
│   ├── list                    # List organizations
│   ├── show ORG_ID             # Show organization
│   ├── create                  # Create organization
│   ├── update ORG_ID           # Update organization
│   └── fetch ORG_ID           # Fetch organization data
│
├── feeds                       # Feed management
│   ├── list                    # List feeds
│   ├── show FEED_ID            # Show feed details
│   ├── create                  # Create feed
│   ├── update FEED_ID          # Update feed
│   ├── delete FEED_ID          # Delete feed
│   ├── fetch FEED_ID           # Fetch feed data
│   └── cache FEED_ID           # Cache feed locally
│
├── servers                     # Server management
│   ├── list                    # List connected servers
│   ├── show SERVER_ID          # Show server details
│   ├── create                  # Add server
│   ├── update SERVER_ID        # Update server
│   ├── delete SERVER_ID        # Remove server
│   └── test SERVER_ID          # Test server connection
│
├── galaxies                    # Galaxy management
│   ├── list                    # List galaxies
│   ├── show GALAXY_ID          # Show galaxy details
│   ├── elements GALAXY_ID      # List galaxy elements
│   └── cluster CLUSTER_ID      # Show cluster details
│
├── warninglists               # Warninglist management
│   ├── list                    # List warninglists
│   ├── show WARNING_ID         # Show warninglist
│   ├── enabled                 # Show enabled warninglists
│   └── check VALUE             # Check value against warninglists
│
├── noticelists                # Noticelist management
│   ├── list                    # List noticelists
│   ├── show NOTICE_ID          # Show noticelist
│   └── enabled                 # Show enabled noticelists
│
├── tags                        # Tag management
│   ├── list                    # List tags
│   ├── show TAG_ID             # Show tag details
│   ├── create                  # Create tag
│   │   ├── --name TEXT         # Tag name
│   │   ├── --color TEXT        # Tag color
│   │   └── --exportable        # Exportable flag
│   ├── update TAG_ID           # Update tag
│   ├── delete TAG_ID           # Delete tag
│   └── attach                  # Attach tag to object
│       ├── --event-id INT      # Event ID
│       ├── --attribute-id INT  # Attribute ID
│       └── --tag-id INT        # Tag ID
│
├── roles                       # Role management
│   ├── list                    # List roles
│   ├── show ROLE_ID            # Show role details
│   └── permissions ROLE_ID     # Show role permissions
│
├── shadow_attributes          # Shadow attribute management
│   ├── list                    # List shadow attributes
│   ├── accept SHADOW_ID        # Accept shadow attribute
│   ├── discard SHADOW_ID       # Discard shadow attribute
│   └── propose EVENT_ID        # Propose change
│
├── audit_logs                 # Audit log management
│   ├── list                    # List audit logs
│   │   ├── --from DATE         # Start date
│   │   ├── --to DATE           # End date
│   │   └── --user TEXT         # User filter
│   └── show LOG_ID             # Show log entry
│
├── search                      # Global search
│   ├── --term TEXT             # Search term
│   ├── --type TEXT             # Object type filter
│   └── --format FORMAT         # Output format
│
├── export                      # Export utilities
│   ├── events                  # Export events
│   │   ├── --format FORMAT     # Export format
│   │   ├── --from DATE         # Start date
│   │   └── --to DATE           # End date
│   ├── stix                    # Export to STIX
│   │   └── --package-id TEXT   # Package ID
│   └── freetext                # Freetext export
│       └── --event-id INT      # Event ID
│
├── import                      # Import utilities
│   ├── json FILE               # Import JSON
│   ├── stix FILE               # Import STIX
│   ├── openioc FILE            # Import IOC
│   └── csv FILE                # Import CSV
│
├── admin                       # Admin commands
│   ├── users                   # User administration
│   ├── organizations           # Organization admin
│   ├── settings               # System settings
│   ├── databases              # Database maintenance
│   └── diagnostics            # System diagnostics
│
├── config                      # Configuration management
│   ├── show                    # Show current config
│   ├── validate                # Validate config file
│   ├── generate               # Generate config file
│   └── edit                    # Edit config interactively
│
└── plugins                     # Plugin management
    ├── list                    # List plugins
    ├── install NAME            # Install plugin
    ├── uninstall NAME          # Uninstall plugin
    └── enable NAME             # Enable plugin
```

### 4.3 Command Examples

```bash
# Event operations
misp-cli events list --limit 50 --org "ACME Corp" --format table
misp-cli events show 1234
misp-cli events create --info "New malware sample" --threat-level 2

# Attribute operations
misp-cli attributes add 1234 --type ip-src --value "192.168.1.1" --category "Network activity"
misp-cli attributes search --type hostname --value "malware.com" --context

# Search operations
misp-cli search --term "ransomware" --type event --format json

# Export operations
misp-cli export stix --from "2024-01-01" --to "2024-12-31" > export.stix

# Import operations
misp-cli import stix malware.stix

# Admin operations
misp-cli admin diagnostics --full
```

---

## 5. Key Classes and Responsibilities

### 5.1 Core Classes

```python
# src/misp_cli/core/client.py

import httpx
from typing import Any, Optional, Dict
from contextlib import asynccontextmanager

class MISPCLient:
    """
    Async HTTP client for MISP API interactions.
    
    Handles authentication, request formatting, and response processing.
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        verify_ssl: bool = True,
        timeout: int = 30,
        output_format: str = "json"
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.output_format = output_format
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get common headers for API requests."""
        return {
            "Authorization": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    
    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                verify=self.verify_ssl,
                timeout=self.timeout,
                headers=self.headers,
            )
        return self._client
    
    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an API request to MISP.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            files: Files to upload
            
        Returns:
            API response as dictionary
            
        Raises:
            MISPAPIError: On API error responses
            MISPConnectionError: On connection failures
        """
        client = await self.get_client()
        url = f"{self.base_url}{endpoint}"
        
        response = await client.request(
            method=method,
            url=url,
            params=params,
            json=data,
            files=files,
        )
        
        return self._handle_response(response)
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """GET request helper."""
        return await self.request("GET", endpoint, params=params)
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """POST request helper."""
        return await self.request("POST", endpoint, data=data, files=files)
    
    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """PUT request helper."""
        return await self.request("PUT", endpoint, data=data)
    
    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """DELETE request helper."""
        return await self.request("DELETE", endpoint, params=params)
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Process API response."""
        # Error handling implementation
```

### 5.2 CLI Application Class

```python
# src/misp_cli/cli/app.py

import typer
from typing import Optional
from rich.console import Console
from misp_cli.core.config import ConfigManager, CLIConfig
from misp_cli.core.client import MISPCLient

app = typer.Typer(
    name="misp-cli",
    help="MISP CLI - Command-line interface for MISP",
    add_completion=False,
)

class MISPApp:
    """
    Main application class managing CLI state and dependencies.
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        profile: Optional[str] = None,
        output_format: Optional[str] = None,
        no_color: bool = False,
        verbose: bool = False,
    ):
        self.console = Console(no_color=no_color)
        self.verbose = verbose
        self.output_format = output_format
        
        # Load configuration
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load()
        
        # Get active profile
        profile_name = profile or self.config.default_profile
        self.profile = self.config.profiles.get(profile_name)
        
        if not self.profile:
            raise MISPConfigurationError(f"Profile '{profile_name}' not found")
        
        # Create MISP client
        self.client = MISPCLient(
            base_url=self.profile.url,
            api_key=self.profile.api_key,
            verify_ssl=self.profile.verify_ssl,
            timeout=self.profile.timeout,
            output_format=output_format or self.profile.output_format,
        )
    
    async def run_async(self):
        """Run the CLI application asynchronously."""
        try:
            await app.async_run()
        finally:
            await self.client.close()
```

### 5.3 Command Modules

```python
# src/misp_cli/cli/commands/events.py

import typer
from typing import Optional
from datetime import date
from misp_cli.cli.app import MISPApp

events_app = typer.Typer(help="Manage MISP events")

@events_app.command("list")
def list_events(
    ctx: typer.Context,
    page: int = typer.Option(1, "-p", "--page", help="Page number"),
    limit: int = typer.Option(50, "-l", "--limit", help="Items per page"),
    search: Optional[str] = typer.Option(None, "-s", "--search", help="Search query"),
    org: Optional[str] = typer.Option(None, "-o", "--org", help="Organization filter"),
    format: str = typer.Option("json", "-f", "--format", help="Output format"),
):
    """
    List MISP events with optional filtering.
    """
    app: MISPApp = ctx.meta["app"]
    
    params = {
        "page": page,
        "limit": limit,
        "search": search,
        "org": org,
    }
    
    response = app.client.get("/events", params=params)
    
    # Format and display output
    formatter = app.get_formatter(format)
    formatter.output(response["events"])

@events_app.command("show")
def show_event(
    ctx: typer.Context,
    event_id: int = typer.Argument(..., help="Event ID to show"),
    context: bool = typer.Option(False, "-c", "--context", help="Include context"),
    format: str = typer.Option("json", "-f", "--format", help="Output format"),
):
    """
    Show details of a specific event.
    """
    app: MISPApp = ctx.meta["app"]
    
    params = {"context": 1} if context else {}
    response = app.client.get(f"/events/{event_id}", params=params)
    
    formatter = app.get_formatter(format)
    formatter.output(response)

@events_app.command("create")
def create_event(
    ctx: typer.Context,
    info: str = typer.Option(..., "-i", "--info", help="Event info"),
    threat_level: int = typer.Option(2, "-t", "--threat-level", min=1, max=4),
    analysis: int = typer.Option(1, "-a", "--analysis", min=0, max=2),
    distribution: int = typer.Option(5, "-d", "--distribution", min=0, max=5),
    event_date: Optional[date] = typer.Option(None, "-e", "--date", help="Event date"),
    format: str = typer.Option("json", "-f", "--format", help="Output format"),
):
    """
    Create a new MISP event.
    """
    app: MISPApp = ctx.meta["app"]
    
    data = {
        "info": info,
        "threat_level_id": threat_level,
        "analysis": analysis,
        "distribution": distribution,
        "date": event_date.isoformat() if event_date else None,
    }
    
    response = app.client.post("/events", data=data)
    
    formatter = app.get_formatter(format)
    formatter.output(response)
```

---

## 6. API Endpoint Mapping

### 6.1 Endpoint Categories

The MISP OpenAPI spec contains the following endpoint categories:

| Category | Description | Endpoints |
|----------|-------------|-----------|
| Events | Event management | CRUD, search, export, publish, sync |
| Attributes | Attribute management | CRUD, add to event, search |
| Objects | MISP object management | CRUD, templates |
| Users | User management | CRUD, profile, settings |
| Organizations | Organization management | CRUD, fetch |
| Roles | Role and permission management | List, show, permissions |
| Feeds | Feed management | CRUD, fetch, cache |
| Servers | Server connections | CRUD, test, sync |
| Galaxies | Galaxy management | List, show, elements |
| Warninglists | Warninglist management | List, show, check |
| Noticelists | Noticelist management | List, show |
| Tags | Tag management | CRUD, attach, detach |
| ShadowAttributes | Shadow attribute proposals | List, accept, discard |
| Taxii | TAXII integration | Feeds, collections |
| DecayingModels | Decaying model management | List, compute |
| Workflows | Workflow management | List, execute |
| Analytics | Event correlation and analytics | Statistics, correlations |
| AuditLogs | System audit logs | List, show |
| Communities | Community management | List, fetch |
| EventDelegations | Event delegation | Create, accept, discard |
| feeds | Feed ingestion | List, ingest |

### 6.2 HTTP Method Mapping

| HTTP Method | CLI Command | Example |
|-------------|-------------|---------|
| GET | `show`, `list`, `get` | `events show 1234` |
| POST | `create`, `add`, `search` | `events create --info "..."` |
| PUT | `update`, `edit` | `events update 1234 --info "..."` |
| DELETE | `delete`, `remove` | `events delete 1234` |

### 6.3 Endpoint to CLI Mapping

```python
# src/misp_cli/core/endpoints.py

from enum import Enum
from typing import Dict, List

class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"

class MISPEndpoint:
    """Represents a MISP API endpoint."""
    
    def __init__(
        self,
        path: str,
        method: HTTPMethod,
        command_name: str,
        description: str,
        parameters: List[Dict] = None,
        request_body: Dict = None,
    ):
        self.path = path
        self.method = method
        self.command_name = command_name
        self.description = description
        self.parameters = parameters or []
        self.request_body = request_body or {}

# Endpoint registry
ENDPOINT_REGISTRY: Dict[str, MISPEndpoint] = {
    # Events
    "events.list": MISPEndpoint(
        path="/events/index",
        method=HTTPMethod.GET,
        command_name="events list",
        description="List all events",
        parameters=[
            {"name": "page", "type": "integer", "location": "query"},
            {"name": "limit", "type": "integer", "location": "query"},
            {"name": "search", "type": "string", "location": "query"},
        ]
    ),
    "events.show": MISPEndpoint(
        path="/events/{event_id}",
        method=HTTPMethod.GET,
        command_name="events show",
        description="Show event details",
        parameters=[
            {"name": "event_id", "type": "integer", "location": "path"},
            {"name": "context", "type": "boolean", "location": "query"},
        ]
    ),
    "events.create": MISPEndpoint(
        path="/events",
        method=HTTPMethod.POST,
        command_name="events create",
        description="Create new event",
        request_body={
            "type": "object",
            "properties": {
                "info": {"type": "string"},
                "threat_level_id": {"type": "integer"},
                "analysis": {"type": "integer"},
                "distribution": {"type": "integer"},
                "date": {"type": "string", "format": "date"},
            }
        }
    ),
    "events.update": MISPEndpoint(
        path="/events/{event_id}",
        method=HTTPMethod.PUT,
        command_name="events update",
        description="Update event",
        parameters=[
            {"name": "event_id", "type": "integer", "location": "path"},
        ],
        request_body={
            "type": "object",
            "properties": {
                "info": {"type": "string"},
                "threat_level_id": {"type": "integer"},
                "analysis": {"type": "integer"},
                "distribution": {"type": "integer"},
            }
        }
    ),
    "events.delete": MISPEndpoint(
        path="/events/{event_id}",
        method=HTTPMethod.DELETE,
        command_name="events delete",
        description="Delete event",
        parameters=[
            {"name": "event_id", "type": "integer", "location": "path"},
        ]
    ),
    # Attributes
    "attributes.list": MISPEndpoint(
        path="/attributes/index",
        method=HTTPMethod.GET,
        command_name="attributes list",
        description="List attributes",
        parameters=[
            {"name": "event_id", "type": "integer", "location": "query"},
            {"name": "type", "type": "string", "location": "query"},
            {"name": "limit", "type": "integer", "location": "query"},
        ]
    ),
    "attributes.add": MISPEndpoint(
        path="/attributes/add/{event_id}",
        method=HTTPMethod.POST,
        command_name="attributes add",
        description="Add attribute to event",
        parameters=[
            {"name": "event_id", "type": "integer", "location": "path"},
        ],
        request_body={
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "value": {"type": "string"},
                "category": {"type": "string"},
                "comment": {"type": "string"},
            }
        }
    ),
    # ... additional endpoints
}
```

### 6.4 OpenAPI Spec Integration

```python
# src/misp_cli/core/openapi_generator.py

import httpx
import json
from typing import Dict, Any, List
from pathlib import Path

class OpenAPISpecGenerator:
    """
    Generates endpoint mappings from MISP OpenAPI specification.
    """
    
    def __init__(self, openapi_url: str):
        self.openapi_url = openapi_url
        self.spec: Dict[str, Any] = {}
    
    async def fetch_spec(self) -> Dict[str, Any]:
        """Fetch OpenAPI spec from MISP instance."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.openapi_url}/openapi")
            response.raise_for_status()
            self.spec = response.json()
        return self.spec
    
    def generate_endpoints(self) -> List[MISPEndpoint]:
        """Generate endpoint objects from OpenAPI spec."""
        endpoints = []
        
        for path, methods in self.spec.get("paths", {}).items():
            for method, details in methods.items():
                endpoint = self._parse_endpoint(path, method, details)
                if endpoint:
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _parse_endpoint(
        self,
        path: str,
        method: str,
        details: Dict[str, Any]
    ) -> MISPEndpoint:
        """Parse a single endpoint from OpenAPI spec."""
        # Implementation details
        pass
    
    def generate_cli_commands(self, output_dir: Path):
        """Generate CLI command files from endpoints."""
        # Generate command modules from endpoints
        pass
```

---

## 7. Error Handling Strategy

### 7.1 Custom Exception Hierarchy

```python
# src/misp_cli/core/exceptions.py

from typing import Optional, Any

class MISPError(Exception):
    """Base exception for MISP CLI errors."""
    
    def __init__(
        self,
        message: str,
        exit_code: int = 1,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code
        self.details = details or {}


class MISPConfigurationError(MISPError):
    """Configuration file or environment errors."""
    exit_code = 2


class MISPAPIError(MISPError):
    """MISP API response errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int,
        response_body: Optional[str] = None,
        error_type: Optional[str] = None,
    ):
        super().__init__(message, exit_code=3)
        self.status_code = status_code
        self.response_body = response_body
        self.error_type = error_type


class MISPConnectionError(MISPError):
    """Network connection errors."""
    exit_code = 4


class MISPAuthenticationError(MISPAPIError):
    """Authentication/authorization errors."""
    exit_code = 5


class MISPValidationError(MISPError):
    """Input validation errors."""
    exit_code = 6


class MISPNotFoundError(MISPAPIError):
    """Resource not found errors."""
    exit_code = 7


class MISPRateLimitError(MISPAPIError):
    """Rate limiting errors."""
    
    def __init__(
        self,
        message: str,
        retry_after: int = 60,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after
        self.exit_code = 8


class MISPOutputError(MISPError):
    """Output formatting errors."""
    exit_code = 9
```

### 7.2 Error Handler

```python
# src/misp_cli/core/error_handler.py

import sys
import traceback
from typing import Any, Callable
from functools import wraps
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from misp_cli.core.exceptions import MISPError

class ErrorHandler:
    """Centralized error handling for the CLI."""
    
    def __init__(self, console: Console, verbose: bool = False):
        self.console = console
        self.verbose = verbose
    
    def handle(self, error: Exception) -> int:
        """
        Handle an exception and return exit code.
        
        Args:
            error: The exception to handle
            
        Returns:
            Exit code to use
        """
        if isinstance(error, MISPError):
            return self._handle_misp_error(error)
        elif isinstance(error, httpx.HTTPError):
            return self._handle_http_error(error)
        else:
            return self._handle_unknown_error(error)
    
    def _handle_misp_error(self, error: MISPError) -> int:
        """Handle MISP-specific errors."""
        panel = Panel(
            Text(error.message, style="bold red"),
            title="Error",
            subtitle=f"Exit code: {error.exit_code}",
        )
        self.console.print(panel)
        
        if self.verbose and error.details:
            self.console.print_json(data=error.details)
        
        return error.exit_code
    
    def _handle_http_error(self, error: httpx.HTTPError) -> int:
        """Handle HTTP errors."""
        error_type = type(error).__name__
        message = f"HTTP Error: {error_type}"
        
        if hasattr(error, "response"):
            status_code = error.response.status_code
            message += f" (Status: {status_code})"
        
        panel = Panel(
            Text(message, style="bold red"),
            title="Connection Error",
            subtitle="Exit code: 4",
        )
        self.console.print(panel)
        
        if self.verbose:
            self.console.print_exception()
        
        return 4
    
    def _handle_unknown_error(self, error: Exception) -> int:
        """Handle unknown errors."""
        message = f"Unexpected error: {type(error).__name__}: {error}"
        
        panel = Panel(
            Text(message, style="bold red"),
            title="Unexpected Error",
            subtitle="Exit code: 1",
        )
        self.console.print(panel)
        
        if self.verbose:
            traceback.print_exc()
        
        return 1

def error_handler(func: Callable) -> Callable:
    """Decorator to apply error handling to a function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            handler = ErrorHandler(console=Console(), verbose=False)
            sys.exit(handler.handle(e))
    return wrapper
```

### 7.3 Common Error Responses

```python
# Error response mapping
ERROR_MAPPINGS = {
    400: MISPValidationError,
    401: MISPAuthenticationError,
    403: MISPAuthenticationError,
    404: MISPNotFoundError,
    405: MISPValidationError,
    429: MISPRateLimitError,
    500: MISPAPIError,
    503: MISPConnectionError,
}

def get_error_class(status_code: int) -> type:
    """Get the appropriate error class for a status code."""
    return ERROR_MAPPINGS.get(status_code, MISPAPIError)
```

---

## 8. Output Formatting

### 8.1 Formatter Interface

```python
# src/misp_cli/cli/formatters/__init__.py

from abc import ABC, abstractmethod
from typing import Any, Dict

class OutputFormatter(ABC):
    """Abstract base class for output formatters."""
    
    def __init__(self, colorize: bool = True):
        self.colorize = colorize
    
    @abstractmethod
    def output(self, data: Any) -> str:
        """Format and return the data."""
        pass
    
    @abstractmethod
    def format_error(self, error: str) -> str:
        """Format an error message."""
        pass


class JSONFormatter(OutputFormatter):
    """JSON output formatter."""
    
    def output(self, data: Any) -> str:
        import json
        return json.dumps(data, indent=2, default=str)
    
    def format_error(self, error: str) -> str:
        import json
        return json.dumps({"error": error}, indent=2)


class TableFormatter(OutputFormatter):
    """Table output formatter using Rich."""
    
    def output(self, data: Any) -> str:
        from rich.table import Table
        from rich.console import Console
        
        if isinstance(data, list):
            return self._format_list(data)
        elif isinstance(data, dict):
            return self._format_dict(data)
        else:
            return str(data)
    
    def _format_list(self, data: list) -> str:
        if not data:
            return "No data available"
        
        table = Table(show_header=True, header_style="bold magenta")
        
        # Add columns from first item
        if isinstance(data[0], dict):
            for key in data[0].keys():
                table.add_column(key.replace("_", " ").title())
            
            for item in data:
                table.add_row(*[str(v) for v in item.values()])
        else:
            table.add_column("Value")
            for item in data:
                table.add_row(str(item))
        
        console = Console()
        with console.capture() as capture:
            console.print(table)
        return capture.get()
    
    def _format_dict(self, data: dict) -> str:
        from rich.table import Table
        from rich.pretty import pretty_repr
        
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="cyan")
        table.add_column("Value")
        
        for key, value in data.items():
            table.add_row(str(key), pretty_repr(value))
        
        console = Console()
        with console.capture() as capture:
            console.print(table)
        return capture.get()
    
    def format_error(self, error: str) -> str:
        from rich.text import Text
        return Text(error, style="bold red").plain


class CSVFormatter(OutputFormatter):
    """CSV output formatter."""
    
    def output(self, data: Any) -> str:
        import csv
        from io import StringIO
        
        if not isinstance(data, list):
            data = [data]
        
        if not data:
            return ""
        
        output = StringIO()
        if isinstance(data[0], dict):
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        else:
            writer = csv.writer(output)
            writer.writerow(data)
        
        return output.getvalue()
    
    def format_error(self, error: str) -> str:
        return f"error\n{error}"


class STIXFormatter(OutputFormatter):
    """STIX/TAXII output formatter."""
    
    def output(self, data: Any) -> str:
        import json
        from stix2 import Package
        
        # Convert MISP data to STIX format
        stix_package = self._misp_to_stix(data)
        return json.dumps(stix_package, indent=2)
    
    def _misp_to_stix(self, data: Any) -> Any:
        """Convert MISP data to STIX format."""
        # Implementation depends on STIX2 library
        pass
    
    def format_error(self, error: str) -> str:
        import json
        return json.dumps({
            "error": error,
            "stix2_objects": []
        }, indent=2)
```

### 8.2 Formatter Selection

```python
# src/misp_cli/cli/app.py (additional methods)

class MISPApp:
    # ... existing code ...
    
    def get_formatter(self, format: str) -> OutputFormatter:
        """Get formatter by name."""
        formatters = {
            "json": JSONFormatter(colorize=False),
            "table": TableFormatter(colorize=self.console.color_system is not None),
            "csv": CSVFormatter(colorize=False),
            "stix": STIXFormatter(colorize=False),
        }
        
        formatter = formatters.get(format)
        if not formatter:
            raise MISPOutputError(f"Unknown output format: {format}")
        
        return formatter
```

---

## 9. Plugin Architecture

### 9.1 Plugin Base Class

```python
# src/misp_cli/plugins/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import typer

class MISPPlugin(ABC):
    """
    Base class for MISP CLI plugins.
    
    Plugins can extend the CLI with custom commands, formatters, or endpoints.
    """
    
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    
    def __init__(self):
        self.app = typer.Typer(help=self.description)
    
    @abstractmethod
    def register(self):
        """
        Register the plugin's commands with the main app.
        
        Override this method to add commands using self.app.command()
        """
        pass
    
    def get_commands(self) -> List[str]:
        """
        Get list of commands provided by this plugin.
        
        Returns:
            List of command names
        """
        return []
    
    def get_endpoints(self) -> Dict[str, Any]:
        """
        Get custom endpoints provided by this plugin.
        
        Returns:
            Dictionary mapping endpoint paths to handlers
        """
        return {}
    
    def get_formatters(self) -> Dict[str, str]:
        """
        Get custom formatters provided by the plugin.
        
        Returns:
            Dictionary mapping format names to formatter classes
        """
        return {}
    
    def initialize(self, misp_app: "MISPApp"):
        """
        Initialize the plugin with the main app context.
        
        Args:
            misp_app: Reference to the main MISPApp instance
        """
        self.misp_app = misp_app
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate plugin-specific configuration.
        
        Args:
            config: Plugin configuration dictionary
            
        Returns:
            True if configuration is valid
        """
        return True
    
    def cleanup(self):
        """Cleanup resources when plugin is unloaded."""
        pass
```

### 9.2 Plugin Registry

```python
# src/misp_cli/plugins/registry.py

from typing import Dict, List, Optional, Type
from misp_cli.plugins.base import MISPPlugin

class PluginRegistry:
    """Registry for managing MISP CLI plugins."""
    
    def __init__(self):
        self._plugins: Dict[str, MISPPlugin] = {}
        self._plugin_classes: Dict[str, Type[MISPPlugin]] = {}
    
    def register(self, plugin_class: Type[MISPPlugin]):
        """Register a plugin class."""
        plugin = plugin_class()
        self._plugin_classes[plugin.name] = plugin_class
        return plugin
    
    def load(self, plugin_name: str) -> Optional[MISPPlugin]:
        """Load a plugin by name."""
        if plugin_name in self._plugins:
            return self._plugins[plugin_name]
        
        plugin_class = self._plugin_classes.get(plugin_name)
        if not plugin_class:
            return None
        
        plugin = plugin_class()
        self._plugins[plugin_name] = plugin
        return plugin
    
    def unload(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if plugin_name in self._plugins:
            plugin = self._plugins[plugin_name]
            plugin.cleanup()
            del self._plugins[plugin_name]
            return True
        return False
    
    def list_plugins(self) -> List[str]:
        """List all registered plugins."""
        return list(self._plugin_classes.keys())
    
    def list_loaded(self) -> List[str]:
        """List all loaded plugins."""
        return list(self._plugins.keys())
```

### 9.3 Plugin Example

```python
# src/misp_cli/plugins/custom_endpoints.py

from misp_cli.plugins.base import MISPPlugin

class CustomEndpointPlugin(MISPPlugin):
    """Example plugin with custom endpoints."""
    
    name = "custom-endpoints"
    version = "1.0.0"
    description = "Custom MISP endpoints plugin"
    author = "Example Author"
    
    def register(self):
        @self.app.command("custom-search")
        def custom_search(query: str):
            """Custom search command."""
            # Implementation
            pass
        
        @self.app.command("bulk-export")
        def bulk_export(
            event_ids: str = typer.Argument(..., help="Comma-separated event IDs"),
            format: str = typer.Option("json", "-f", "--format"),
        ):
            """Bulk export events."""
            # Implementation
            pass
```

---

## 10. Implementation Roadmap

### 10.1 Phase 1: Core Foundation (Week 1)

1. **Project Setup**
   - Initialize pyproject.toml with dependencies
   - Set up uv virtual environment
   - Configure type hints and mypy
   - Set up pre-commit hooks

2. **Configuration System**
   - Implement ConfigManager class
   - Support INI file parsing with pydantic
   - Environment variable overrides
   - Profile validation

3. **HTTP Client**
   - Implement MISPCLient with httpx
   - Authentication header handling
   - Request/response processing
   - Error handling integration

### 10.2 Phase 2: CLI Framework (Week 2)

1. **Main Application**
   - Set up Typer app
   - Global options and context
   - Plugin system integration
   - Output formatter selection

2. **Command Modules**
   - Events commands (CRUD, list, search)
   - Attributes commands
   - Users and Organizations
   - Tags and Galaxies

3. **Output Formatters**
   - JSON formatter
   - Table formatter (Rich)
   - CSV formatter
   - STIX formatter (optional)

### 10.3 Phase 3: Full API Coverage (Week 3)

1. **Complete Endpoint Mapping**
   - Generate endpoints from OpenAPI spec
   - Implement all remaining commands
   - Error response handling
   - Request validation

2. **Advanced Features**
   - Search functionality
   - Export/Import utilities
   - Admin commands
   - Diagnostics

3. **Plugin System**
   - Plugin base class
   - Plugin registry
   - Plugin discovery mechanism

### 10.4 Phase 4: Testing and Documentation (Week 4)

1. **Testing**
   - Unit tests for core modules
   - Integration tests with mock MISP
   - CLI command testing
   - Error handling tests

2. **Documentation**
   - README with examples
   - Installation guide
   - Configuration documentation
   - Command reference

3. **Polishing**
   - Shell completion setup
   - Error message improvements
   - Performance optimization
   - Final code review

### 10.5 Key Files to Create

```
Phase 1:
├── pyproject.toml
├── src/misp_cli/core/config.py
├── src/misp_cli/core/client.py
├── src/misp_cli/core/exceptions.py
└── src/misp_cli/__main__.py

Phase 2:
├── src/misp_cli/cli/app.py
├── src/misp_cli/cli/options.py
├── src/misp_cli/cli/commands/events.py
├── src/misp_cli/cli/commands/attributes.py
└── src/misp_cli/cli/formatters/__init__.py

Phase 3:
├── src/misp_cli/core/endpoints.py
├── src/misp_cli/core/openapi_generator.py
├── src/misp_cli/cli/commands/*.py (remaining commands)
├── src/misp_cli/plugins/base.py
└── src/misp_cli/plugins/registry.py

Phase 4:
├── tests/unit/*
├── tests/integration/*
├── docs/*
└── README.md
```

---

## Appendix A: MISP API Reference

### A.1 Event Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/events/index` | GET | List events |
| `/events/view/{id}` | GET | View event |
| `/events/add` | POST | Create event |
| `/events/edit/{id}` | POST | Edit event |
| `/events/delete/{id}` | POST | Delete event |
| `/events/publish/{id}` | POST | Publish event |
| `/events/unpublish/{id}` | POST | Unpublish event |
| `/events/export` | GET | Export event |
| `/events/restSearch` | POST | Advanced search |

### A.2 Attribute Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/attributes/index` | GET | List attributes |
| `/attributes/view/{id}` | GET | View attribute |
| `/attributes/add/{event_id}` | POST | Add attribute |
| `/attributes/edit/{id}` | POST | Edit attribute |
| `/attributes/delete/{id}` | POST | Delete attribute |
| `/attributes/restSearch` | POST | Search attributes |

### A.3 User Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/users/index` | GET | List users |
| `/users/view/{id}` | GET | View user |
| `/users/add` | POST | Create user |
| `/users/edit/{id}` | POST | Edit user |
| `/users/delete/{id}` | POST | Delete user |
| `/users/current` | GET | Current user info |
| `/users/login` | POST | Login |
| `/users/logout` | POST | Logout |

---

## Appendix B: Configuration Examples

### B.1 Minimal Config

```ini
[default]
url = https://misp.local
api_key = your-api-key
```

### B.2 Full Config

```ini
[DEFAULT]
verify_ssl = true
timeout = 60
output_format = table
colorize = true

[production]
url = https://misp.production.local
api_key = prod-api-key
verify_ssl = true
timeout = 60
output_format = table

[development]
url = https://misp.dev.local
api_key = dev-api-key
verify_ssl = false
timeout = 30
output_format = json

[ci-cd]
url = https://misp.ci.local
api_key = ci-api-key
verify_ssl = true
timeout = 120
output_format = json
```

### B.3 Environment Variables

```bash
export MISP_CLI_CONFIG=~/.misp-cli.conf
export MISP_CLI_PROFILE=production
export MISP_CLI_OUTPUT_FORMAT=table
export MISP_CLI_VERBOSE=true
```

---

## Appendix C: Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | MISP API error |
| 4 | Network/connection error |
| 5 | Authentication error |
| 6 | Validation error |
| 7 | Resource not found |
| 8 | Rate limit exceeded |
| 9 | Output formatting error |

---

*Document Version: 1.0*  
*Last Updated: 2024*  
*Author: MISP CLI Architecture Team*
