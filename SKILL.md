# misp-cli Skills Reference

A quick-reference guide to everything `misp-cli` can do.

---

## Global Options

These options apply to every command:

| Option | Short | Description |
|---|---|---|
| `--config PATH` | `-c` | Path to config file |
| `--profile NAME` | `-p` | Named profile to use |
| `--debug` | `-d` | Show API request details |
| `--no-color` | | Disable colored output |
| `--help` | `-h` | Show help |

---

## Configuration

```bash
misp-cli config --generate           # Create a default ~/.misp-cli.conf
misp-cli config --show               # Show active profile details
misp-cli config --validate           # Validate the config file
misp-cli config --set-default NAME   # Change the default profile
```

**Config file location** (first match wins):

1. `--config` flag
2. `MISP_CLI_CONFIG` env var
3. `~/.misp-cli.conf`
4. `./.misp-cli.conf`

**Environment variable overrides:**

| Variable | Effect |
|---|---|
| `MISP_CLI_URL` | Override instance URL |
| `MISP_CLI_API_KEY` | Override API key |
| `MISP_CLI_VERIFY_SSL` | Override SSL verification |
| `MISP_CLI_TIMEOUT` | Override request timeout |
| `MISP_CLI_OUTPUT_FORMAT` | Override output format |
| `MISP_CLI_PROFILE` | Override active profile |

**Sample config:**

```ini
[DEFAULT]
default_profile = default
verify_ssl = true
timeout = 30
output_format = json

[profile:default]
url = https://misp.example.com
api_key = your-api-key-here
```

---

## Output Formats

All list/show commands support three output modes:

| Flag | Format |
|---|---|
| *(default)* | JSON |
| `--json` | JSON (explicit) |
| `--table` / `-t` | Rich table |
| `--csv` | CSV |

The profile's `output_format` setting applies when no flag is given.

---

## Commands

### `version`

```bash
misp-cli version    # Show the connected MISP server version
```

---

### `events`

```bash
misp-cli events list                              # List events (default: 50, sorted by timestamp desc)
misp-cli events list --limit 10 --page 2
misp-cli events list --search "ransomware"
misp-cli events list --org "ACME Corp"
misp-cli events list --from 2024-01-01 --to 2024-03-19
misp-cli events list --last 7d                   # Relative time (5d, 12h, 30m)
misp-cli events list --tag "threat-report"
misp-cli events list --count                     # Print count only
misp-cli events list --minimal                   # Minimal fields

misp-cli events show 1234                        # Show a single event
misp-cli events show 1234 --context              # Include context

misp-cli events create --info "Title"
misp-cli events create --info "Title" --threat-level 1   # 1=High 2=Medium 3=Low 4=Undefined
misp-cli events create --info "Title" --analysis 0       # 0=Initial 1=Ongoing 2=Completed
misp-cli events create --info "Title" --distribution 0   # 0-5 (see --help)

misp-cli events delete 1234
misp-cli events delete 1234 --force              # Skip confirmation

misp-cli events publish 1234
misp-cli events unpublish 1234

misp-cli events search "malware"
misp-cli events search "APT" --from 2024-01-01 --count

misp-cli events export 1234                      # Export as JSON (default)
misp-cli events export 1234 --format csv         # json | csv | xml | stix | misp2

misp-cli events attributes 1234                  # List attributes of an event

# Preferred command for fetching the latest event(s) — do NOT use `events list --limit 1`
misp-cli events latest                           # Latest 1 event
misp-cli events latest --count 5
misp-cli events latest --tags "tag1,tag2"
misp-cli events latest --orgs "ACME Corp"
misp-cli events latest --eventid                 # Sort by event ID instead of timestamp
misp-cli events latest --verbose                 # Full event details
```

---

### `attributes`

```bash
misp-cli attributes list
misp-cli attributes show ATTR_ID
misp-cli attributes add --event-id 1234 --type ip-dst --value 1.2.3.4
misp-cli attributes edit ATTR_ID
misp-cli attributes delete ATTR_ID
misp-cli attributes search "term"
misp-cli attributes types       # List all valid attribute types
misp-cli attributes categories  # List all valid attribute categories
```

---

### `tags`

```bash
misp-cli tags list
misp-cli tags show TAG_ID
misp-cli tags search "term"
misp-cli tags create --name "my-tag"
misp-cli tags edit TAG_ID
misp-cli tags delete TAG_ID
misp-cli tags attach --event-id 1234 --tag-id TAG_ID
misp-cli tags detach --event-id 1234 --tag-id TAG_ID
misp-cli tags event-tags EVENT_ID
```

---

### `users`

```bash
misp-cli users list
misp-cli users show USER_ID
misp-cli users current          # Show your own user
misp-cli users create --email user@example.com --org-id 1 --role-id 3
misp-cli users edit USER_ID
misp-cli users delete USER_ID
misp-cli users org-users ORG_ID
misp-cli users admin USER_ID    # Toggle admin status
misp-cli users disable USER_ID
misp-cli users enable USER_ID
```

---

### `organisations`

```bash
misp-cli organisations list
misp-cli organisations show ORG_ID
misp-cli organisations create --name "Org Name"
misp-cli organisations edit ORG_ID
misp-cli organisations delete ORG_ID
```

---

### `servers`

```bash
misp-cli servers list
misp-cli servers show SERVER_ID
misp-cli servers create --name "Peer" --url https://peer.example.com --api-key KEY
misp-cli servers edit SERVER_ID
misp-cli servers delete SERVER_ID
misp-cli servers pull SERVER_ID    # Pull events from peer
misp-cli servers push SERVER_ID    # Push events to peer
misp-cli servers test SERVER_ID    # Test connectivity
misp-cli servers sync SERVER_ID    # Bidirectional sync
misp-cli servers status            # Server sync status
```

---

### `feeds`

```bash
misp-cli feeds list
misp-cli feeds show FEED_ID
misp-cli feeds create --name "Feed" --url https://...
misp-cli feeds edit FEED_ID
misp-cli feeds delete FEED_ID
misp-cli feeds fetch FEED_ID    # Fetch latest data
misp-cli feeds cache FEED_ID    # Cache feed locally
misp-cli feeds enable FEED_ID
misp-cli feeds disable FEED_ID
misp-cli feeds import           # Import default MISP feeds
misp-cli feeds test FEED_ID
```

### `manage-feeds`

```bash
misp-cli manage-feeds list
misp-cli manage-feeds show FEED_ID
misp-cli manage-feeds create
misp-cli manage-feeds edit FEED_ID
misp-cli manage-feeds delete FEED_ID
misp-cli manage-feeds enable FEED_ID
misp-cli manage-feeds disable FEED_ID
misp-cli manage-feeds fetch FEED_ID
misp-cli manage-feeds cache FEED_ID
misp-cli manage-feeds test FEED_ID
misp-cli manage-feeds import
misp-cli manage-feeds export
```

---

### `objects`

```bash
misp-cli objects list
misp-cli objects show OBJECT_ID
misp-cli objects add --event-id 1234 --template-name "domain-ip"
misp-cli objects edit OBJECT_ID
misp-cli objects delete OBJECT_ID
misp-cli objects references OBJECT_ID
misp-cli objects add-reference --object-id OBJ_ID --ref-id REF_ID --relationship "related-to"
misp-cli objects event-objects EVENT_ID
```

### `object-templates`

```bash
misp-cli object-templates list
misp-cli object-templates show TEMPLATE_ID
misp-cli object-templates delete TEMPLATE_ID
misp-cli object-templates import FILE
misp-cli object-templates export TEMPLATE_ID
```

---

### `galaxies`

```bash
misp-cli galaxies list
misp-cli galaxies show GALAXY_ID
misp-cli galaxies elements GALAXY_ID
misp-cli galaxies cluster CLUSTER_ID
misp-cli galaxies search "term"
misp-cli galaxies attach --event-id 1234 --cluster-id CLUSTER_ID
misp-cli galaxies detach --event-id 1234 --cluster-id CLUSTER_ID
misp-cli galaxies event-galaxies EVENT_ID
```

---

### `sharing-groups`

```bash
misp-cli sharing-groups list
misp-cli sharing-groups show GROUP_ID
misp-cli sharing-groups create --name "Group Name"
misp-cli sharing-groups edit GROUP_ID
misp-cli sharing-groups delete GROUP_ID
misp-cli sharing-groups add-org GROUP_ID --org-id ORG_ID
misp-cli sharing-groups remove-org GROUP_ID --org-id ORG_ID
misp-cli sharing-groups add-server GROUP_ID --server-id SERVER_ID
misp-cli sharing-groups remove-server GROUP_ID --server-id SERVER_ID
```

---

### `taxonomies`

```bash
misp-cli taxonomies list
misp-cli taxonomies show TAXONOMY_ID
misp-cli taxonomies enable TAXONOMY_ID
misp-cli taxonomies disable TAXONOMY_ID
misp-cli taxonomies toggle TAXONOMY_ID
misp-cli taxonomies import
misp-cli taxonomies delete TAXONOMY_ID
misp-cli taxonomies tags TAXONOMY_ID
```

### `warninglists`

```bash
misp-cli warninglists list
misp-cli warninglists show LIST_ID
misp-cli warninglists enable LIST_ID
misp-cli warninglists disable LIST_ID
misp-cli warninglists toggle LIST_ID
misp-cli warninglists check VALUE    # Check a value against all warninglists
misp-cli warninglists import
misp-cli warninglists delete LIST_ID
```

### `noticelists`

```bash
misp-cli noticelists list
misp-cli noticelists show LIST_ID
misp-cli noticelists enable LIST_ID
misp-cli noticelists disable LIST_ID
misp-cli noticelists toggle LIST_ID
misp-cli noticelists import
misp-cli noticelists delete LIST_ID
```

---

### `roles`

```bash
misp-cli roles list
misp-cli roles show ROLE_ID
misp-cli roles permissions ROLE_ID
```

---

### `decaying-models`

```bash
misp-cli decaying-models list
misp-cli decaying-models show MODEL_ID
misp-cli decaying-models enable MODEL_ID
misp-cli decaying-models disable MODEL_ID
misp-cli decaying-models import
misp-cli decaying-models export MODEL_ID
misp-cli decaying-models delete MODEL_ID
```

---

### `event-blocklists`

```bash
misp-cli event-blocklists list
misp-cli event-blocklists add --comment "reason"
misp-cli event-blocklists add-uuid UUID
misp-cli event-blocklists add-id EVENT_ID
misp-cli event-blocklists remove BLOCKLIST_ID
misp-cli event-blocklists bulk-add --file uuids.txt
misp-cli event-blocklists cleanup    # Remove expired entries
```

---

### `logs`

```bash
misp-cli logs list
misp-cli logs list --limit 100 --page 2
misp-cli logs search "term"
misp-cli logs user USER_ID
misp-cli logs event EVENT_ID
misp-cli logs date --from 2024-01-01 --to 2024-03-31
misp-cli logs clear    # Clear audit log
```

---

### `news`

```bash
misp-cli news list
misp-cli news show NEWS_ID
misp-cli news create --title "Title" --message "Body"
misp-cli news edit NEWS_ID
misp-cli news delete NEWS_ID
misp-cli news publish NEWS_ID
misp-cli news unpublish NEWS_ID
```

---

### `stats`

```bash
misp-cli stats system   # System statistics
misp-cli stats users    # User statistics
misp-cli stats orgs     # Organisation statistics
misp-cli stats tags     # Tag usage statistics
```

---

## Common Patterns

```bash
# Use a specific profile
misp-cli --profile production events list

# Debug: show API calls being made
misp-cli --debug events list

# Get machine-readable output
misp-cli events list --json | jq '.[] | .id'

# Pipe CSV into a spreadsheet tool
misp-cli events list --csv > events.csv

# Count events matching a search
misp-cli events search "ransomware" --count

# Get the 5 most recently modified events
misp-cli events latest --count 5

# Filter events by tag (last 7 days)
misp-cli events list --tag "tlp:red" --last 7d
```
