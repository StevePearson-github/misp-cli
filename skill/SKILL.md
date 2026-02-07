---
name: misp-cli
description: Command-line interface for MISP (Malware Information Sharing Platform). Use when interacting with MISP instances for threat intelligence operations, event management, attribute handling, tag management, feed operations, and server administration. Supports multiple profiles, JSON/table/CSV output, and automation integration.
---

# MISP CLI Skill

This skill provides capabilities for interacting with MISP (Malware Information Sharing Platform) through a comprehensive command-line interface.

## Description

The MISP CLI is a command-line tool that enables security teams, threat intelligence analysts, and incident responders to efficiently manage and interact with MISP instances directly from the terminal. MISP is an open-source threat intelligence platform used for collecting, sharing, storing, and correlating Indicators of Compromise (IOCs) from targeted attacks, threat intelligence, and cybersecurity data.

This CLI provides complete coverage of the MISP REST API, allowing users to perform all standard operations including event management, attribute handling, tag management, feed operations, and server administration without leaving their terminal environment.

## Key Features and Capabilities

### Complete MISP API Coverage
- **Events**: Create, read, update, delete, publish, and search for security events
- **Attributes**: Manage individual indicators of compromise within events (IP addresses, domains, hashes, URLs, etc.)
- **Objects**: Work with structured MISP objects containing multiple related attributes
- **Tags**: Apply, search, and manage tags for categorization and correlation
- **Feeds**: Fetch and manage threat intelligence feeds from external sources
- **Servers**: Administer connected MISP server instances
- **Galaxies**: Explore and utilize threat actor and malware galaxy clusters

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

## Common Use Cases

### Threat Intelligence Operations
```bash
# Search for specific threat indicators across all events
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli events search "APT29"

# List recent malware-related events
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli events list --limit 100

# Extract all IP addresses from a specific event
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli events attributes 1234 | jq '.[].value'
```

### Incident Response
```bash
# Quick lookup of an IOC during an active investigation
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli attributes search "192.168.1.1"

# Create a new event for an ongoing incident
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli events create --info "Incident-2024-001" --threat-level 1

# Tag an event with incident classification
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli tags attach --event-id 1234 --tag-id 5678
```

### Threat Intelligence Sharing
```bash
# Export an event for sharing with partner organizations
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli events export 1234 --format json

# Manage internal tags for consistent categorization
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli tags create --name "Actionable" --color "#00ff00" --exportable

# Fetch and integrate external threat feeds
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli feeds fetch feed-id
```

### MISP Administration
```bash
# Monitor connected MISP instances
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli servers list

# Check MISP server version and health
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli version

# Validate current configuration
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli config --validate
```

### Automation and Integration
```bash
# Script integration with JSON output
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli --output json events list > today_events.json

# CI/CD pipeline integration for threat feed updates
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli --profile production feeds fetch all
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
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli attributes list --from 2024-01-01 --to 2024-12-31

# Search for events modified in the last 7 days
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli events search --last 7d

# List objects created in Q1 2024
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli objects list --from 2024-01-01T00:00:00Z --to 2024-03-31T23:59:59Z

# Find events by exact date
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli events list --date 2024-06-15

# Search for attributes with specific timestamp
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli attributes search "malware" --from 2024-01-01

# Use Unix timestamp for precise filtering
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli events list --from 1672531200 --to 1704067199
```

### Combining Filters

Date filters can be combined with other filtering options:

```bash
# Filter by date range and organization
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli events list --from 2024-01-01 --org "ACME Corp"

# Search for IP attributes in a time range
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli attributes list --type "ip-src" --from 2024-01-01 --to 2024-06-30

# Last modified with event filter
cd ~/.kilocode/skills/misp-cli/scripts && uv run misp-cli objects list --event 1234 --last 30d
```

## Running the CLI

The MISP CLI skill is installed in `~/.kilocode/skills/misp-cli/` with the following structure:

```
~/.kilocode/skills/misp-cli/
├── scripts/
│   ├── pyproject.toml      # Project configuration for uv
│   ├── README.md          # Project README
│   └── src/
│       └── misp_cli/        # The CLI package
├── SKILL.md                 # This skill definition
└── README.md               # Skill README
```

To run the CLI, navigate to the scripts directory and use uv:

```bash
cd ~/.kilocode/skills/misp-cli/scripts
uv run misp-cli <command>

# Examples:
uv run misp-cli events list
uv run misp-cli attributes search "192.168.1.1"
uv run misp-cli --profile production servers list
```

## Important MISP Concepts and Terminology

### Events
The core unit of information in MISP. An event represents a security incident, threat report, or piece of threat intelligence. Events contain metadata (timestamp, threat level, analysis status, distribution settings) and are composed of attributes and objects. Events can be published to make them visible to other MISP instances within sharing groups.

### Attributes
Individual indicators of compromise attached to events. Attributes represent specific pieces of threat intelligence such as:
- **IP addresses**: `ip-src`, `ip-dst`
- **Domain names**: `domain`, `hostname`
- **File hashes**: `md5`, `sha1`, `sha256`, `sha512`
- **URLs**: `url`
- **Email addresses**: `email-src`, `email-dst`
- **File paths**: `filename`, `filepath`
- **Mutex identifiers**: `mutex`

Attributes have a type (what kind of indicator), a category (how it's used in the attack chain), and a value (the actual indicator).

### Objects
Structured collections of related attributes that describe a specific entity (malware sample, phishing campaign, tool, vulnerability). Objects provide better context and standardization compared to loose attributes.

### Tags
Labels used to categorize and organize events and attributes. Tags enable:
- **Workflow classification**: `workflow-status="complete"`, `workflow-phase="analysis"`
- **Threat actor attribution**: `Threat-Actor="APT29"`, `Threat-Actor="Lazarus-Group"`
- **Malware identification**: `Malware="LockBit"`, `Malware="Emotet"`
- **TLPs classification**: `TLP:AMBER`, `TLP:GREEN`
- **Confidence levels**: `confidence-level="high"`

### Feeds
External or internal sources of threat intelligence that can be fetched into MISP. Feeds provide standardized threat data from commercial providers, ISACs, community sources, or internal teams.

### Galaxies
Pre-defined collections of threat intelligence clusters including:
- **Threat actors**: Named APT groups, criminal organizations
- **Malware families**: Known malware strains and variants
- **Attack patterns**: MITRE ATT&CK techniques
- **Vulnerabilities**: CVEs and security advisories

### Distribution Levels
Control how widely information is shared:
- **Your Organization Only**: Private to the MISP instance
- **This Community**: Shared with connected communities
- **Connected Communities**: Shared with all connected MISP instances
- **All Communities**: Publicly visible to all MISP users

### Sharing Groups
Define specific sets of MISP instances that can access certain events, enabling selective sharing with partners while maintaining confidentiality.

### Warninglists
Lists of known values that should not generate alerts (RFC1918 addresses, common DNS resolvers, etc.) to reduce false positives.

### Taxonomies
Classification schemes for organizing and tagging threat intelligence using standardized vocabularies.

### Threat Levels
Classification of event severity:
- **High**: Indicates sophisticated threats requiring immediate attention
- **Medium**: Significant threats requiring timely review
- **Low**: Minor threats or informational events
- **Undefined**: Not yet classified

### Analysis Status
Current state of event investigation:
- **Initial**: New event awaiting analysis
- **Ongoing**: Active investigation in progress
- **Completed**: Analysis finished
- **Deferred**:暂缓处理
