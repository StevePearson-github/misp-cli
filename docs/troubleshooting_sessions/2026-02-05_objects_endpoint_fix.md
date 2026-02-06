# Troubleshooting Session: MISP API Endpoint Fixes

**Date:** 2026-02-05  
**Time:** 03:03 UTC  
**Issue:** Multiple misp-cli commands return "Not Found" errors

## Problems Identified

### 1. Objects List Command

**Command:**
```bash
misp-cli --profile rocky objects list
```

**Error:**
```
Error: Not Found: Resource '/objects/index' not found
```

**Root Cause:** The MISP API doesn't have an `/objects/index` endpoint.

**Solution:** Changed the endpoint from `/objects/index` to `/objects/restSearch` in [`src/misp_cli/cli/commands/objects.py`](src/misp_cli/cli/commands/objects.py:82).

### 2. Users List Command

**Command:**
```bash
misp-cli --profile rocky users list
```

**Error:**
```
Error: Not Found: Resource '/users/index' not found
```

**Root Cause:** The `/users/index` endpoint doesn't exist in MISP. User listing requires admin privileges and uses a different endpoint.

**Solution:** Changed the endpoint from `/users/index` to `/admin/users/index` (POST request) in [`src/misp_cli/cli/commands/users.py`](src/misp_cli/cli/commands/users.py:79).

### 3. Users Org-Users Command

**Command:**
```bash
misp-cli --profile rocky users org-users <org_id>
```

**Error:**
```
Error: Not Found: Resource '/users/index' not found
```

**Solution:** Changed the endpoint from `/users/index` to `/admin/users/index` (POST request) in [`src/misp_cli/cli/commands/users.py`](src/misp_cli/cli/commands/users.py:256).

### 4. Response Parsing Fix

**Issue:** The `/admin/users/index` endpoint returns a direct array instead of a dict with keys.

**Solution:** Updated response parsing to handle both array and dict responses:

```python
users = response if isinstance(response, list) else response.get("User", response.get("users", response.get("data", [])))
```

## Files Updated

1. [`src/misp_cli/cli/commands/objects.py`](src/misp_cli/cli/commands/objects.py) - Line 82
2. [`src/misp_cli/cli/commands/users.py`](src/misp_cli/cli/commands/users.py) - Lines 79, 256, 82, 259

## Verification

All fixed commands now work correctly:

```bash
$ misp-cli --profile rocky objects list
[]

$ misp-cli --profile rocky users list
[
  {
    "User": {...},
    "Role": {...},
    "Organisation": {...}
  },
  ...
]
```

## MISP API Endpoint Patterns Discovered

Based on testing, the MISP REST API uses these patterns:

| Resource | List Endpoint | Notes |
|----------|--------------|-------|
| Events | `/events/index` | Standard pattern |
| Attributes | `/attributes/index` | Standard pattern |
| Tags | `/tags/index` | Standard pattern |
| Galaxies | `/galaxies/index` | Standard pattern |
| Warninglists | `/warninglists/index` | Standard pattern |
| Roles | `/roles/index` | Standard pattern |
| Users | `/admin/users/index` | POST required, admin only |
| Objects | `/objects/restSearch` | Unique exception |

## Commands Not Fixed

### decaying-models list

**Error:** `Error: Not Found: Resource '/decayingModels/index' not found`

**Status:** The decaying models feature appears to not be enabled on this MISP instance. The `/decayingModels/index` endpoint follows the standard MISP API pattern, but the feature may not be installed.
