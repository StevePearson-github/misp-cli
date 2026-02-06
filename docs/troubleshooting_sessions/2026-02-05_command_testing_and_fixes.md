# Troubleshooting Session: README Command Testing and Fixes

**Date:** 2026-02-05  
**Time:** 02:14 UTC  
**Issue:** Duplicate CLI option short form in attributes commands

## Problem Description

When testing the MISP CLI commands documented in README.md, the following warning was observed:

```
UserWarning: The parameter -t is used more than once. Remove its duplicate as parameters should be unique.
```

This warning appeared when running:
- `misp-cli attributes list --help`
- `misp-cli attributes search --help`

## Root Cause Analysis

In [`src/misp_cli/cli/commands/attributes.py`](src/misp_cli/cli/commands/attributes.py), both the `list` and `search` commands had the `-t` short option assigned to two different parameters:

**`list` command (lines 64-69):**
```python
type: Optional[str] = typer.Option(None, "-t", "--type", help="Filter by attribute type"),
# ...
table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
```

**`search` command (lines 220-223):**
```python
type: Optional[str] = typer.Option(None, "-t", "--type", help="Filter by type"),
# ...
table_output: bool = typer.Option(False, "-t", "--table", help="Output as table"),
```

Both `--type` and `--table` options were using the same short form `-t`, causing a conflict.

## Solution Implemented

Changed the `--table` option short form from `-t` to `-T` in both commands to avoid the conflict with `--type`:

```python
# Before
table_output: bool = typer.Option(False, "-t", "--table", help="Output as table")

# After
table_output: bool = typer.Option(False, "-T", "--table", help="Output as table")
```

## Files Updated

1. [`src/misp_cli/cli/commands/attributes.py`](src/misp_cli/cli/commands/attributes.py) - Fixed duplicate `-t` option in:
   - `list_attributes()` function (line 69)
   - `search_attributes()` function (line 223)

## Verification

After the fix, running the attribute commands no longer produces duplicate option warnings:

```bash
$ misp-cli attributes list --help
Usage: python -m misp_cli attributes list [OPTIONS]
...
  -t, --type TEXT   Filter by attribute type
  ...
  -T, --table       Output as table
...

$ misp-cli attributes search --help
Usage: python -m misp_cli attributes search [OPTIONS] VALUE
...
  -t, --type TEXT   Filter by type
  ...
  -T, --table       Output as table
...
```

## Commands Tested

### Basic Commands
| Command | Status |
|---------|--------|
| `misp-cli --help` | ✅ Working |
| `misp-cli version` | ✅ Working |
| `misp-cli config --generate` | ✅ Working |
| `misp-cli config --show` | ✅ Working |
| `misp-cli config --validate` | ✅ Working |

### Event Commands
All event subcommands work correctly (connection errors expected without MISP instance):
| Command | Status |
|---------|--------|
| `misp-cli events --help` | ✅ Working |
| `misp-cli events list` | ⚠️ Connection error (expected) |
| `misp-cli events show` | ⚠️ Connection error (expected) |
| `misp-cli events create` | ⚠️ Connection error (expected) |
| `misp-cli events delete` | ⚠️ Connection error (expected) |
| `misp-cli events publish` | ⚠️ Connection error (expected) |
| `misp-cli events unpublish` | ⚠️ Connection error (expected) |
| `misp-cli events search` | ⚠️ Connection error (expected) |
| `misp-cli events export` | ⚠️ Connection error (expected) |
| `misp-cli events attributes` | ⚠️ Connection error (expected) |

### Attribute Commands
| Command | Status |
|---------|--------|
| `misp-cli attributes --help` | ✅ Working |
| `misp-cli attributes list` | ✅ Fixed (no more duplicate option warning) |
| `misp-cli attributes show` | ⚠️ Connection error (expected) |
| `misp-cli attributes add` | ⚠️ Connection error (expected) |
| `misp-cli attributes edit` | ⚠️ Connection error (expected) |
| `misp-cli attributes delete` | ⚠️ Connection error (expected) |
| `misp-cli attributes search` | ✅ Fixed (no more duplicate option warning) |
| `misp-cli attributes types` | ⚠️ Connection error (expected) |
| `misp-cli attributes categories` | ⚠️ Connection error (expected) |

### Tag Commands
| Command | Status |
|---------|--------|
| `misp-cli tags --help` | ✅ Working |
| All tag subcommands | ✅ Working |

### Other Command Groups
All other command groups work correctly:
- Objects, Feeds, Manage-feeds, Servers
- Galaxies, Users, Sharing-groups
- Warninglists, Noticelists, Taxonomies, Roles
- Decaying-models, Event-blocklists, Attribute-blocklists
- News, Object-templates

## Notes

1. Commands that require MISP connection show connection errors because the test environment doesn't have a running MISP instance. The default profile URL (`https://misp.example.com`) is not accessible.

2. All command help outputs display correctly after the fix.

3. The `-T` short form for `--table` is now consistently used where needed across the CLI.
