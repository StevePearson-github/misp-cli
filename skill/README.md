# MISP CLI Skill

A command-line interface skill for interacting with MISP (Malware Information Sharing Platform) instances, enabling threat intelligence operations, event management, and server administration.

## What is the MISP CLI Skill?

The MISP CLI skill provides capabilities for interacting with MISP through a comprehensive command-line interface. MISP is an open-source threat intelligence platform used for collecting, sharing, storing, and correlating Indicators of Compromise (IOCs) from targeted attacks, threat intelligence, and cybersecurity data.

This skill enables security teams, threat intelligence analysts, and incident responders to efficiently manage and interact with MISP instances directly from the terminal, with complete coverage of the MISP REST API.

## Features

### Complete MISP API Coverage
- **Events**: Create, read, update, delete, publish, and search for security events
- **Attributes**: Manage individual indicators of compromise within events (IP addresses, domains, hashes, URLs, etc.)
- **Objects**: Work with structured MISP objects containing multiple related attributes
- **Tags**: Apply, search, and manage tags for categorization and correlation
- **Feeds**: Fetch and manage threat intelligence feeds from external sources
- **Servers**: Administer connected MISP server instances
- **Galaxies**: Explore and utilize threat actor and malware galaxy clusters

### Additional Commands
- **Users**: Manage user accounts and permissions
- **Roles**: Handle role-based access control
- **Taxonomies**: Work with classification schemes
- **Noticelists**: Manage notice lists
- **Warninglists**: Handle known values that shouldn't generate alerts
- **Sharing Groups**: Manage selective sharing configurations
- **Blocklists**: Manage event and attribute blocklists
- **Decaying Models**: Handle indicator decay models
- **News**: Access MISP instance news
- **Object Templates**: Work with object template definitions

### Multiple Profile Support
- Configure multiple MISP instances (production, staging, sandbox)
- Switch between profiles with a single CLI option
- Support for environment variable overrides
- Configuration validation and generation tools

### Flexible Output Formatting
- JSON output for programmatic integration
- Table output for human-readable terminal display
- CSV export for spreadsheet compatibility
- Colored output with Rich library integration

### Developer-Friendly Features
- Type-safe Python codebase with Pydantic validation
- Modern CLI built with Typer
- Comprehensive help system
- Verbose mode for debugging

## Requirements

### Prerequisites
- **Python 3.8+**: The skill is built with Python
- **uv Package Manager**: Recommended for installation (but pip also works)
- **MISP Instance**: Access to a MISP server (local or remote)
- **API Key**: Valid MISP API authentication credentials

### Python Dependencies
The skill requires the following core dependencies:
- `typer` - CLI framework
- `requests` - HTTP client for API calls
- `pydantic` - Data validation
- `rich` - Terminal output formatting
- `pyyaml` - Configuration file parsing

## Installation

### Method 1: Local Installation (Development)

Install directly from the source code for development or customization:

```bash
# Clone the repository (if not already cloned)
git clone <repository-url>
cd misp-cli

# Install with uv (recommended)
uv tool install .

# Or with pip
pip install -e .
```

### Method 2: Distributable Package Installation

Create and install a distributable `.skill` package:

#### Step 1: Create the Package

**Using the Python script:**
```bash
python scripts/install_skill.py --package
```

**Using the Bash script:**
```bash
chmod +x scripts/install_skill.sh
./scripts/install_skill.sh --package
```

This creates a `misp-cli.skill` file in the `./dist` directory.

#### Step 2: Install the Package

**Using the Python script (automatic install + package):**
```bash
python scripts/install_skill.py --package
```

This installs to: `~/.kilocode/skills/misp-cli/`

**Using the Bash script:**
```bash
./install_skill.sh
```

**Custom output directory:**
```bash
python scripts/install_skill.py --package --output-dir /tmp/packages
./install_skill.sh --package --output-dir /tmp/packages
```

### Method 3: Manual Installation

Copy the skill files manually:

```bash
# Create the skills directory
mkdir -p ~/.kilocode/skills/misp-cli

# Copy skill files
cp -r skill/* ~/.kilocode/skills/misp-cli/
```

## Using the Installer Scripts

### Python Installer (`scripts/install_skill.py`)

```bash
# Basic installation
python scripts/install_skill.py

# Install and create a .skill package
python scripts/install_skill.py --package

# Install with custom output directory
python scripts/install_skill.py --package --output-dir /tmp/packages

# Show help
python scripts/install_skill.py --help
```

### Bash Installer (`scripts/install_skill.sh`)

```bash
# Make executable
chmod +x scripts/install_skill.sh

# Basic installation
./scripts/install_skill.sh

# Install and create a .skill package
./scripts/install_skill.sh --package

# Install with custom output directory
./scripts/install_skill.sh --package --output-dir /tmp/packages

# Show help
./scripts/install_skill.sh --help
```

### What the Installers Do

1. **Detect Project Structure**: Automatically finds the skill source directory
2. **Copy Files**: Copies skill files to `~/.kilocode/skills/misp-cli/`
3. **Create Package**: Optionally creates a distributable `.skill` package (zip format)
4. **Filter Files**: Excludes unwanted files (.git, __pycache__, .pyc, .swp, .swo)
5. **Verify Installation**: Confirms successful installation

### Post-Installation

After installation, restart Claude or refresh your session to use the skill.

Verify installation:
```bash
cat ~/.kilocode/skills/misp-cli/SKILL.md
```

## Usage Examples

### Threat Intelligence Operations
```bash
# Search for specific threat indicators across all events
misp-cli events search "APT29"

# List recent malware-related events
misp-cli events list --limit 100

# Extract all IP addresses from a specific event
misp-cli events attributes 1234 | jq '.[].value'
```

### Incident Response
```bash
# Quick lookup of an IOC during an active investigation
misp-cli attributes search "192.168.1.1"

# Create a new event for an ongoing incident
misp-cli events create --info "Incident-2024-001" --threat-level 1

# Tag an event with incident classification
misp-cli tags attach --event-id 1234 --tag-id 5678
```

### Threat Intelligence Sharing
```bash
# Export an event for sharing with partner organizations
misp-cli events export 1234 --format json

# Manage internal tags for consistent categorization
misp-cli tags create --name "Actionable" --color "#00ff00" --exportable

# Fetch and integrate external threat feeds
misp-cli feeds fetch feed-id
```

### MISP Administration
```bash
# Monitor connected MISP instances
misp-cli servers list

# Check MISP server version and health
misp-cli version

# Validate current configuration
misp-cli config --validate
```

### Automation and Integration
```bash
# Script integration with JSON output
misp-cli --output json events list > today_events.json

# CI/CD pipeline integration for threat feed updates
misp-cli --profile production feeds fetch all
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

## Configuration

### Profile Configuration
Create a `.misp-cli.conf` file with your MISP instance details:

```ini
[default]
url = https://misp.example.com
api_key = your-api-key-here
ssl_verify = true

[production]
url = https://misp.production.com
api_key = production-api-key
ssl_verify = true

[staging]
url = https://misp.staging.com
api_key = staging-api-key
ssl_verify = false
```

### Environment Variables
Override configuration with environment variables:
- `MISP_URL` - MISP instance URL
- `MISP_API_KEY` - API authentication key
- `MISP_SSL_VERIFY` - SSL verification (true/false)

## MISP Concepts

### Events
The core unit of information in MISP. An event represents a security incident, threat report, or piece of threat intelligence.

### Attributes
Individual indicators of compromise:
- **IP addresses**: `ip-src`, `ip-dst`
- **Domain names**: `domain`, `hostname`
- **File hashes**: `md5`, `sha1`, `sha256`
- **URLs**: `url`
- **Email addresses**: `email-src`, `email-dst`

### Tags
Labels for categorization:
- **Workflow**: `workflow-status="complete"`
- **Threat actors**: `Threat-Actor="APT29"`
- **TLP**: `TLP:AMBER`, `TLP:GREEN`

### Distribution Levels
- Your Organization Only
- This Community
- Connected Communities
- All Communities

### Threat Levels
- **High**: Sophisticated threats requiring immediate attention
- **Medium**: Significant threats requiring timely review
- **Low**: Minor threats or informational events
- **Undefined**: Not yet classified

## Support

For issues and feature requests:
- Check the main [README.md](../../README.md)
- Review [ARCHITECTURE.md](../../docs/ARCHITECTURE.md)
- Review [IMPROVEMENTS.md](../../docs/IMPROVEMENTS.md)

## License

See [LICENSE.md](../../LICENSE.md) for details.
