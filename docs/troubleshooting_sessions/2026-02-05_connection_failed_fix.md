# Troubleshooting Session: Connection failed error for all commands

**Date:** 2026-02-05  
**Issue:** All `misp-cli` commands were failing with error: `[Errno 8] nodename nor servname provided, or not known`

## Symptom

```
(misp-cli) steve@Steves-MacBook-Pro misp-cli % misp-cli events attributes 1
Error: Connection failed: [Errno 8] nodename nor servname provided, or not known
```

## Investigation

1. **Verified curl worked:** The same URL worked with curl but failed in Python
2. **Checked config file:** Found `.misp-cli.conf` had placeholder URL `https://misp.example.com`
3. **Discovered profile flag:** The `--profile rocky` flag was being passed but not used by commands

## Root Cause

All command files in [`src/misp_cli/cli/commands/`](../../src/misp_cli/cli/commands/) were creating their own `MISPConfig` instance via `MISPConfig.from_file()` instead of using the global `MISPApp` instance initialized with `--profile rocky` in [`app.py`](../../src/misp_cli/cli/app.py).

This meant each command was:
1. Not using the profile specified on the command line
2. Reading the default config (which had placeholder values)

### Before (Broken Pattern)

```python
from misp_cli.core.config import MISPConfig
from misp_cli.core.client import MISPCLient

config = MISPConfig.from_file()  # Always reads default, ignores --profile
client = MISPCLient(base_url=config.url, ...)
```

### After (Fixed Pattern)

```python
from misp_cli.cli.app import get_app

app = get_app()  # Gets the global MISPApp with profile
config = app.profile
client = app.client
```

## Files Fixed

| File | Status |
|------|--------|
| [`attributes.py`](../../src/misp_cli/cli/commands/attributes.py) | Fixed |
| [`decaying_models.py`](../../src/misp_cli/cli/commands/decaying_models.py) | Fixed |
| [`event_blocklists.py`](../../src/misp_cli/cli/commands/event_blocklists.py) | Fixed |
| [`attribute_blocklists.py`](../../src/misp_cli/cli/commands/attribute_blocklists.py) | Fixed |
| [`events.py`](../../src/misp_cli/cli/commands/events.py) | Fixed |
| [`feeds.py`](../../src/misp_cli/cli/commands/feeds.py) | Fixed |
| [`feeds_manage_feeds.py`](../../src/misp_cli/cli/commands/feeds_manage_feeds.py) | Fixed |
| [`galaxies.py`](../../src/misp_cli/cli/commands/galaxies.py) | Fixed |
| [`news.py`](../../src/misp_cli/cli/commands/news.py) | Fixed |
| [`noticelists.py`](../../src/misp_cli/cli/commands/noticelists.py) | Fixed |
| [`object_templates.py`](../../src/misp_cli/cli/commands/object_templates.py) | Fixed |
| [`objects.py`](../../src/misp_cli/cli/commands/objects.py) | Fixed |
| [`roles.py`](../../src/misp_cli/cli/commands/roles.py) | Fixed |
| [`servers.py`](../../src/misp_cli/cli/commands/servers.py) | Fixed |
| [`sharing_groups.py`](../../src/misp_cli/cli/commands/sharing_groups.py) | Fixed |
| [`tags.py`](../../src/misp_cli/cli/commands/tags.py) | Fixed |
| [`taxonomies.py`](../../src/misp_cli/cli/commands/taxonomies.py) | Fixed |
| [`users.py`](../../src/misp_cli/cli/commands/users.py) | Fixed |
| [`warninglists.py`](../../src/misp_cli/cli/commands/warninglists.py) | Fixed |

## Verification

Command `misp-cli --profile rocky events attributes 1` now returns expected data:

```json
[
  {
    "id": 1,
    "type": "ip-dst",
    "category": "Network activity",
    "to_ids": false,
    "uuid": "ddb6b55b-64fe-4189-9d3f-28b15267366d",
    "event_id": 1,
    "distribution": 5,
    "timestamp": 1768791449,
    "comment": "",
    "sharing_group_id": 0,
    "deleted": false,
    "disable_correlation": false,
    "object_id": 0,
    "object_relation": null,
    "first_seen": null,
    "last_seen": null,
    "value": "4.4.4.4",
    "Galaxy": [],
    "ShadowAttribute": []
  }
]
```

## Lessons Learned

1. **Global State Pattern:** Commands should use `get_app()` to access the global `MISPApp` instance instead of creating their own config
2. **Profile Handling:** The `--profile` flag in `app.py` initializes the global app, but commands need to reference it via `get_app()`
3. **Testing:** Always verify with the same profile flag that users would use in production
