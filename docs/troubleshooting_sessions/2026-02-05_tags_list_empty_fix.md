# Troubleshooting Session: Tags List Returns Nothing

**Date:** 2026-02-05  
**Time:** 02:10 UTC  
**Issue:** `misp-cli tags list` returns empty array `[]` even though tags exist in MISP

## Problem Description

When running `misp-cli tags list --json`, the command returned an empty array `[]` instead of the actual tags:

```bash
$ python -m misp_cli.cli.app tags list --json
[]
```

## Root Cause Analysis

The MISP API response for `/tags/index` uses `Tag` (singular) as the key, but the code was looking for `tags` (plural) or `data`.

### API Response Structure

```python
# What the API returns:
{
    "Tag": [
        {"id": 3, "name": "estimative-language:likelihood-probability=\"almost-certain\"", ...},
        {"id": 1, "name": "estimative-language:likelihood-probability=\"likely\"", ...},
        ...
    ]
}

# What the code was looking for:
tags = response.get("tags", response.get("data", []))
# Returns: [] because "tags" and "data" keys don't exist
```

### Affected Code

The issue was in [`src/misp_cli/cli/commands/tags.py`](src/misp_cli/cli/commands/tags.py) in two places:

1. [`list_tags()`](src/misp_cli/cli/commands/tags.py:84) function
2. [`search_tags()`](src/misp_cli/cli/commands/tags.py:133) function

## Solution Implemented

Updated the response parsing to check for `Tag` key first:

```python
# Before:
tags = response.get("tags", response.get("data", []))

# After:
tags = response.get("Tag", response.get("tags", response.get("data", [])))
```

### Files Modified

1. [`src/misp_cli/cli/commands/tags.py`](src/misp_cli/cli/commands/tags.py) - Line 84 and 133

## Verification

After the fix, the command correctly returns all tags:

```bash
$ python -m misp_cli.cli.app tags list --json
[
  {
    "id": 3,
    "name": "estimative-language:likelihood-probability=\"almost-certain\"",
    "colour": "#001fc2",
    "exportable": true,
    ...
  },
  {
    "id": 1,
    "name": "estimative-language:likelihood-probability=\"likely\"",
    "colour": "#001899",
    "exportable": true,
    ...
  },
  ...
]
```

Table output also works correctly:

```bash
$ python -m misp_cli.cli.app tags list --table
┏━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━┳━━━━━┳━━━━┳━━━━━┳━━━━┳━━━━━┳━━━━┓
┃ Id ┃ Name ┃ Colour ┃ Exportable ┃ Org Id ┃ User Id ┃ Hide Tag ┃ ... ┃
┡━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━╇━━━━━╇━━━━╇━━━━━╇━━━━╇━━━━━╇━━━━┩
│ 3  │ es… │ #001fc2 │ True  │ 0   │ 0   │ False │ ... │
│ 1  │ es… │ #001899 │ True  │ 0   │ 0   │ False │ ... │
│ 4  │ es… │ #001585 │ True  │ 0   │ 0   │ False │ ... │
│ 5  │ es… │ #001270 │ True  │ 0   │ 0   │ False │ ... │
│ 2  │ es… │ #001cad │ True  │ 0   │ 0   │ False │ ... │
│ 6  │ st… │ #388e3e │ False │ 0   │ 0   │ False │ ... │
└────┴─────┴─────┴─────┴─────┴─────┴─────┴────┴─────┴────┴─────┴────┴─────┴────┘
```

## Notes

- The MISP API uses inconsistent response formats across different endpoints
- Some endpoints use plural keys (`events`, `attributes`), while others use singular (`Tag`, `Event`)
- When adding new commands, always verify the actual API response structure before implementing
