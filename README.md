# MISP CLI

A comprehensive command-line interface for interacting with [MISP](https://www.misp-project.org/) (Malware Information Sharing Platform). This CLI tool enables security teams to efficiently manage events, attributes, tags, feeds, and other MISP entities directly from the terminal.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Available Commands](#available-commands)
- [Examples](#examples)
- [Date Filtering](#date-filtering)
- [Development](#development)
- [License](#license)

## Features

- **Complete MISP API Coverage**: Full support for events, attributes, objects, tags, users, feeds, servers, galaxies, and more
- **Multiple Profiles**: Configure and switch between multiple MISP instances (production, staging, sandbox)
- **Flexible Output**: Support for JSON, table, and CSV output formats
- **Rich Formatting**: Beautiful terminal output using Rich library
- **Environment Variables**: Override configuration via environment variables
- **Type-Safe**: Fully typed Python codebase with Pydantic validation
- **Modern CLI**: Built with Typer for a clean, intuitive command structure

## Installation

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/StevePearson-github/misp-cli.git
cd misp-cli

# Install using uv (recommended)
uv tool install .

# Or install using pip
pip install .
```

### Install Development Dependencies

```bash
# Install with development dependencies using uv
uv install --dev .

# Or with pip
pip install -e ".[dev]"
```

### Verify Installation

```bash
misp-cli --help
```

## Shell Completion

The CLI supports shell completion for commands and options.

### Install Completions Permanently

```bash
# For bash
misp-cli --install-completion bash

# For zsh
misp-cli --install-completion zsh

# For fish
misp-cli --install-completion fish
```

### Use Completions Temporarily

```bash
# For bash
source <(misp-cli --show-completion bash)

# For zsh
eval "$(misp-cli --show-completion zsh)"

# For fish
misp-cli --show-completion fish | source
```

## Configuration

### Configuration File

The CLI uses an INI-style configuration file (`.misp-cli.conf`) that supports multiple profiles for different MISP instances.

**Configuration File Locations** (in order of precedence):
1. `--config` CLI parameter (highest priority)
2. `MISP_CLI_CONFIG` environment variable
3. `~/.misp-cli.conf` (user home directory)
4. `./.misp-cli.conf` (current working directory)

### Example Configuration

```ini
; MISP CLI Configuration File
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
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `url` | string | - | Base URL of MISP instance |
| `api_key` | string | - | MISP API authentication key |
| `verify_ssl` | boolean | `true` | Enable/disable SSL verification |
| `timeout` | integer | `30` | Request timeout in seconds (1-300) |
| `output_format` | string | `json` | Default output format (json, table, csv) |
| `colorize` | boolean | `true` | Enable colored terminal output |

### Environment Variable Overrides

Override configuration settings using environment variables:

```bash
export MISP_CLI_URL="https://misp.example.com"
export MISP_CLI_API_KEY="your-api-key"
export MISP_CLI_VERIFY_SSL="true"
export MISP_CLI_TIMEOUT="30"
export MISP_CLI_OUTPUT_FORMAT="json"
export MISP_CLI_PROFILE="production"
```

### Generate Default Configuration

Generate a default configuration file:

```bash
misp-cli config --generate
```

### Validate Configuration

Check if your configuration is valid:

```bash
misp-cli config --validate
```

## Usage

### Global Options

```bash
misp-cli [OPTIONS] COMMAND [ARGS]...
```

| Option | Description |
|--------|-------------|
| `-c, --config FILE` | Path to configuration file |
| `-p, --profile TEXT` | Profile name to use from configuration |
| `--no-color` | Disable colored output |
| `-h, --help` | Show help message |
| `--install-completion` | Install shell completion for the current shell |
| `--show-completion` | Show shell completion to copy or customize installation |

### Basic Commands

```bash
# Show MISP server version
misp-cli version

# Show current configuration
misp-cli config --show

# Use a specific profile
misp-cli --profile production events list

# Override output format
misp-cli --output table events list
```

## Available Commands

### Event Management

| Command | Description |
|---------|-------------|
| [`events list`](##examples) | List events with pagination and filtering |
| [`events show`](##examples) | Show details of a specific event |
| [`events create`](##examples) | Create a new event |
| [`events delete`](##examples) | Delete an event |
| [`events publish`](##examples) | Publish an event |
| [`events unpublish`](##examples) | Unpublish an event |
| [`events search`](##examples) | Search for events |
| [`events export`](##examples) | Export an event |
| [`events attributes`](##examples) | List attributes of an event |

### Attribute Management

| Command | Description |
|---------|-------------|
| [`attributes list`](##examples) | List attributes with optional filtering |
| [`attributes show`](##examples) | Show details of a specific attribute |
| [`attributes add`](##examples) | Add an attribute to an event |
| [`attributes edit`](##examples) | Edit an attribute |
| [`attributes delete`](##examples) | Delete an attribute |
| [`attributes search`](##examples) | Search for attributes by value |
| [`attributes types`](##examples) | List all available attribute types |
| [`attributes categories`](##examples) | List all available attribute categories |

### Tag Management

| Command | Description |
|---------|-------------|
| [`tags list`](##examples) | List all tags |
| [`tags show`](##examples) | Show details of a specific tag |
| [`tags search`](##examples) | Search for tags by name |
| [`tags create`](##examples) | Create a new tag |
| [`tags edit`](##examples) | Edit a tag |
| [`tags delete`](##examples) | Delete a tag |
| [`tags attach`](##examples) | Attach a tag to an event or attribute |
| [`tags detach`](##examples) | Detach a tag from an event or attribute |
| [`tags event-tags`](##examples) | List all tags for an event |

### Object Management

| Command | Description |
|---------|-------------|
| `objects list` | List objects |
| `objects show` | Show object details |
| `objects create` | Create a new object |
| `objects delete` | Delete an object |
| `objects templates` | List object templates |

### Feed Management

| Command | Description |
|---------|-------------|
| `feeds list` | List feeds |
| `feeds show` | Show feed details |
| `feeds fetch` | Fetch feed data |
| `manage-feeds list` | List managed feeds |
| `manage-feeds enable` | Enable a managed feed |
| `manage-feeds disable` | Disable a managed feed |

### Server Management

| Command | Description |
|---------|-------------|
| `servers list` | List connected servers |
| `servers show` | Show server details |
| `servers version` | Show MISP server version |
| `servers add` | Add a server connection |
| `servers edit` | Edit a server |
| `servers delete` | Remove a server |
| `servers test` | Test server connection |

### Galaxy Management

| Command | Description |
|---------|-------------|
| `galaxies list` | List galaxies |
| `galaxies show` | Show galaxy details |
| `galaxies elements` | List galaxy elements |

### User Management

| Command | Description |
|---------|-------------|
| `users list` | List users |
| `users show` | Show user details |
| `users current` | Get current user info |

### Organisation Management

| Command | Description |
|---------|-------------|
| `organisations list` | List all organisations |
| `organisations show` | Show organisation details |
| `organisations create` | Create a new organisation |
| `organisations edit` | Edit an organisation |
| `organisations delete` | Delete an organisation |

### Sharing Groups

| Command | Description |
|---------|-------------|
| `sharing-groups list` | List sharing groups |
| `sharing-groups show` | Show sharing group details |

### Log Management

| Command | Description |
|---------|-------------|
| `logs list` | List MISP logs with optional filters |
| `logs search` | Search logs by title or description |
| `logs user` | Get logs for a specific user |
| `logs model` | Get logs for a specific model type |

### Other Commands

| Command | Description |
|---------|-------------|
| `warninglists list` | List warninglists |
| `warninglists show` | Show warninglist details |
| `warninglists enabled` | Show enabled warninglists |
| `noticelists list` | List noticelists |
| `taxonomies list` | List taxonomies |
| `roles list` | List roles |
| `decaying-models list` | List decaying models |
| `event-blocklists list` | List event blocklists |
| `news list` | List news |
| `stats system` | System statistics |
| `stats users` | User statistics |
| `stats orgs` | Organisation statistics |
| `stats tags` | Tag statistics |

## Examples

### Event Operations

```bash
# List events with pagination
misp-cli events list --limit 50 --page 1

# List events from a specific organization
misp-cli events list --org "ACME Corp"

# Search for events
misp-cli events search "ransomware"

# Show event details
misp-cli events show 1234

# Create a new event
misp-cli events create --info "New malware sample" --threat-level 2

# Publish an event
misp-cli events publish 1234

# Export an event as JSON
misp-cli events export 1234 --format json

# List attributes for an event
misp-cli events attributes 1234 --table
```

### Attribute Operations

```bash
# List attributes with filtering
misp-cli attributes list --event 1234 --type "ip-src"

# Show attribute details
misp-cli attributes show 5678

# Add an attribute to an event
misp-cli attributes add 1234 --type "ip-src" --value "192.168.1.1" --category "Network activity"

# Search for attributes by value
misp-cli attributes search "malware.com"

# List available attribute types
misp-cli attributes types

# List available attribute categories
misp-cli attributes categories
```

### Tag Operations

```bash
# List tags
misp-cli tags list --limit 100

# Search for tags
misp-cli tags search "APT"

# Create a new tag
misp-cli tags create --name "APT29" --color "#ff6600" --exportable

# Attach a tag to an event
misp-cli tags attach --event-id 1234 --tag-id 5678

# Detach a tag from an event
misp-cli tags detach --event-id 1234 --tag-id 5678

# List tags for an event
misp-cli tags event-tags 1234
```

### Organisation Operations

```bash
# List organisations
misp-cli organisations list --limit 50

# List organisations in table format
misp-cli organisations list --table

# Show organisation details
misp-cli organisations show 1

# Show organisation by UUID
misp-cli organisations show c99506a6-1255-4b71-afa5-7b8ba48c3b1b

# Create a new organisation
misp-cli organisations create --name "ACME Corp" --sector "Technology" --nationality "US"

# Create organisation with domain restrictions
misp-cli organisations create -n "Example Org" --type "Commercial" --restricted-to-domain "example.com,example.org"

# Edit an organisation
misp-cli organisations edit 1 --name "New Name" --description "Updated description"

# Edit organisation sector and nationality
misp-cli organisations edit 1 --sector "Finance" --nationality "UK"

# Delete an organisation (with confirmation)
misp-cli organisations delete 1

# Delete organisation without confirmation
misp-cli organisations delete 1 --force
```

### Using Different Profiles

```bash
# Use production profile
misp-cli --profile production events list

# Use staging profile with table output
misp-cli --profile staging --output table events list

# Use sandbox profile without color
misp-cli --profile sandbox --no-color events list
```

### Server Operations

```bash
# Show MISP server version
misp-cli version

# List connected servers
misp-cli servers list --limit 50

# Test server connection
misp-cli servers test

# Show server details
misp-cli servers show 1
```

### Output Format Examples

```bash
# JSON output (default)
misp-cli events list

# Table output
misp-cli events list --table

# Force JSON output
misp-cli events list --json

# Override output format globally
misp-cli --output table events list
```

### Log Operations

```bash
# List all logs with pagination
misp-cli logs list --limit 50 --page 1

# Filter logs by model type
misp-cli logs list --model Event

# Filter logs by action
misp-cli logs list --action add

# Filter logs by user email
misp-cli logs list --email admin@example.com

# Filter logs by organisation
misp-cli logs list --org "ACME Corp"

# Filter logs by IP address
misp-cli logs list --ip 192.168.1.1

# Search logs by title
misp-cli logs search "event published"

# Get logs for a specific user
misp-cli logs user 1

# Get logs for a specific model type
misp-cli logs model Event

# Output logs in table format
misp-cli logs list --table

# Output logs as JSON
misp-cli logs list --json
```

### Statistics Operations

```bash
# Get system statistics
misp-cli stats system

# Get user statistics
misp-cli stats users

# Get organisation statistics
misp-cli stats orgs

# Get tag statistics
misp-cli stats tags
```

## Date Filtering

All search commands support powerful date filtering options to help you find events, attributes, and objects within specific time ranges.

### Date Filtering Parameters

| Parameter | Description |
|-----------|-------------|
| `--from` / `--to` | Date range filters (inclusive) |
| `--last` | Relative time filter (e.g., `7d`, `14d`, `5h`, `30m`) |
| `--date` | Event/Object date filter |
| `--timestamp` | Modification timestamp filter |
| `--publish-timestamp` | Publication timestamp filter |

### Supported Date Formats

- **Relative**: `7d`, `14d`, `30d`, `5h`, `30m` (days, hours, minutes)
- **ISO 8601**: `2024-03-19T11:10:24Z`, `2024-03-19T00:00:00`
- **Unix timestamp**: `1617875568`
- **Date only**: `2024-03-19`

### Examples

```bash
# List attributes from a specific date range
misp-cli attributes list --from 2024-01-01 --to 2024-12-31

# Search for events modified in the last 7 days
misp-cli events search --last 7d

# List objects created in Q1 2024
misp-cli objects list --from 2024-01-01T00:00:00Z --to 2024-03-31T23:59:59Z

# Find events by exact date
misp-cli events list --date 2024-06-15

# Search for attributes with specific timestamp
misp-cli attributes search "malware" --from 2024-01-01

# Use Unix timestamp for precise filtering
misp-cli events list --from 1672531200 --to 1704067199
```

### Combining Filters

Date filters can be combined with other filtering options:

```bash
# Filter by date range and organization
misp-cli events list --from 2024-01-01 --org "ACME Corp"

# Search for IP attributes in a time range
misp-cli attributes list --type "ip-src" --from 2024-01-01 --to 2024-06-30

# Last modified with event filter
misp-cli objects list --event 1234 --last 30d
```

## Development

### Project Structure

```
misp-cli/
├── pyproject.toml          # Project configuration
├── README.md              # This file
├── src/
│   └── misp_cli/
│       ├── __init__.py    # Package initialization
│       ├── __main__.py     # Entry point
│       ├── cli/
│       │   ├── app.py      # Main CLI application
│       │   └── commands/   # Command modules
│       └── core/
│           ├── client.py   # MISP API client
│           ├── config.py  # Configuration management
│           └── exceptions.py
├── tests/                  # Test suite
└── docs/                   # Documentation
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=misp_cli

# Run specific test file
pytest tests/test_events.py
```

### Code Quality

```bash
# Run linting
ruff check src/misp_cli/

# Format code
black src/misp_cli/

# Type checking
mypy src/misp_cli/
```

### Adding New Commands

To add a new command module:

1. Create a new file in `src/misp_cli/cli/commands/`
2. Define a Typer app for your commands
3. Import and register the app in `src/misp_cli/cli/app.py`

Example command structure:

```python
import typer
from misp_cli.core.client import MISPCLient
from misp_cli.core.config import MISPConfig

myapp = typer.Typer(help="Manage my resource")

@myapp.command("list")
def list_resources():
    """List resources."""
    config = MISPConfig.from_file()
    client = MISPCLient(
        base_url=config.url,
        api_key=config.api_key,
        verify_ssl=config.verify_ssl,
    )
    # Your implementation here
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues and feature requests, please use the [GitHub Issues](https://github.com/StevePearson-github/misp-cli/issues) page.

---

Built with ❤️ for the threat intelligence community
