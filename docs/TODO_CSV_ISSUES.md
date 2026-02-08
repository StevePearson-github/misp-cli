# CSV Output Issues - TODO

This document tracks issues found during CSV output testing for misp-cli commands.

## High Priority

### 1. roles list --csv - Minimal Data Output
**Status:** Open  
**Issue:** The `roles list --csv` command returns only IDs, not the full role data.

**Command:**
```bash
uv run misp-cli roles list --csv
```

**Expected:** Full role data with columns like `id`, `name`, `permissions`, etc.  
**Actual:** Returns:
```
Role
42
42
42
42
```

**Root Cause:** The MISP API returns data with a nested structure that needs to be unwrapped. Similar to how `noticelists.py` uses `_unwrap_nested_data()`, the `roles.py` file may need the same treatment.

**Fix Needed:** Add `_unwrap_nested_data()` helper to `src/misp_cli/cli/commands/roles.py` and unwrap the roles data.

---

### 2. attribute-blocklists - 404 Not Found
**Status:** Open  
**Issue:** The `attribute-blocklists list --csv` command fails with API endpoint not found.

**Command:**
```bash
uv run misp-cli attribute-blocklists list --csv
```

**Error:**
```
Error: Not Found: Resource '/attributeBlocklists/index' not found
```

**Root Cause:** The MISP API endpoint may use a different URL pattern (e.g., `/attribute_blocklists/index` with underscores instead of camelCase).

**Fix Needed:** Verify the correct API endpoint in MISP documentation and update `src/misp_cli/cli/commands/attribute_blocklists.py` accordingly.

---

### 3. decaying-models - 404 Not Found
**Status:** Open  
**Issue:** The `decaying-models list --csv` command fails with API endpoint not found.

**Command:**
```bash
uv run misp-cli decaying-models list --csv
```

**Error:**
```
Error: Not Found: Resource '/decayingModels/index' not found
```

**Root Cause:** The MISP API endpoint may use a different URL pattern or this feature may not be available in all MISP versions.

**Fix Needed:** Verify the correct API endpoint in MISP documentation and update `src/misp_cli/cli/commands/decaying_models.py` accordingly.

---

## Medium Priority

### 4. logs list --csv - Nested Data Not Unwrapped
**Status:** Open  
**Issue:** The `logs list --csv` command shows nested "Log" key instead of flat data.

**Command:**
```bash
uv run misp-cli logs list --csv --limit 2
```

**Actual Output:**
```
Log
12
12
```

**Expected:** Flat log data with columns like `id`, `title`, `action`, `email`, etc.

**Root Cause:** The logs response has a nested structure `{"Log": {...}}` that needs to be unwrapped.

**Fix Needed:** Add `_unwrap_nested_data()` helper to `src/misp_cli/cli/commands/logs.py` and unwrap the logs data.

---

### 5. news list --csv - MISP Internal Error
**Status:** Open  
**Issue:** The `news list --csv` command fails with an internal error.

**Command:**
```bash
uv run misp-cli news list --csv
```

**Error:**
```
Error: An Internal Error Has Occurred.: An Internal Error Has Occurred.
```

**Root Cause:** Unknown - could be a permission issue, API version mismatch, or MISP configuration issue.

**Fix Needed:** 
1. Check MISP server logs for more details
2. Verify the user has permission to access news
3. Check if the news feature is enabled in MISP configuration

---

## Low Priority / Future Enhancements

### 6. warninglists list --csv - Minimal Data
**Status:** Low Priority  
**Issue:** The `warninglists list --csv` command shows limited data.

**Command:**
```bash
uv run misp-cli warninglists list --csv
```

**Actual Output:**
```
Warninglist
10
10
10
10
```

**Note:** Similar issue to roles - data may be nested.

---

## Completed Items

### 9. Blank Line Inconsistencies Fixed ✅
**Status:** Done  
**Action:** Fixed extra blank lines in CSV output blocks in `src/misp_cli/cli/commands/taxonomies.py` and `src/misp_cli/cli/commands/warninglists.py`.

**Before:**
```python
    if output_format == "csv":


        _print_csv(taxonomies)


    if output_format == "table":
```

**After:**
```python
    if output_format == "csv":
        _print_csv(taxonomies)
    elif output_format == "table":
```

---

### 10. Shared Output Module Created ✅
**Status:** Done  
**Action:** Created `src/misp_cli/cli/output.py` with shared output utilities to reduce code duplication.

**Functions exported:**
- `get_output_format()` - Determine output format based on options and config
- `print_csv()` - Print data as CSV
- `print_json()` - Print data as formatted JSON
- `print_table()` - Print data as a table using Rich
- `unwrap_nested_data()` - Unwrap nested MISP API response data

**Files updated to use shared module:**
- `src/misp_cli/cli/commands/tags.py`
- `src/misp_cli/cli/commands/users.py`
- `src/misp_cli/cli/commands/organisations.py`
- `src/misp_cli/cli/commands/taxonomies.py`
- `src/misp_cli/cli/commands/warninglists.py`

---

### 7. -o csv Global Option - REMOVED ✅
**Status:** Done  
**Action:** Removed the broken `-o`/`--output` option from `src/misp_cli/cli/app.py`.

**Reason:** The global `-o` option was broken (never actually used by commands) and redundant since all commands now have `--csv`, `--json`, and `--table` options.

**Updated Usage:** Use command-specific options instead:
```bash
# JSON output (default)
uv run misp-cli events list

# Table output
uv run misp-cli events list --table

# CSV output
uv run misp-cli events list --csv
```

---

### 8. Code Review Bug Fixes ✅
**Status:** Done  
**Action:** Fixed multiple undefined variable bugs in CSV output functions.

**Bugs Fixed:**
- `src/misp_cli/cli/commands/attribute_blocklists.py:117` - Changed `attribute_blocklists` to `entries`
- `src/misp_cli/cli/commands/objects.py:273` - Changed `objects` to `references` in `list_references`
- `src/misp_cli/cli/commands/decaying_models.py:117` - Changed `decaying_models` to `models`
- `src/misp_cli/cli/commands/galaxies.py:188` - Changed `galaxies` to `elements` in `list_elements`
- `src/misp_cli/cli/commands/news.py:117` - Changed `news` to `news_items`

**Testing Results:**
```bash
uv run misp-cli roles list --csv     # Works (shows Role IDs)
uv run misp-cli tags list --csv      # Works (full tag data)
uv run misp-cli users list --csv      # Works (full user data)
uv run misp-cli objects list --csv   # Works (empty - no objects)
uv run misp-cli taxonomies list --csv # Works (taxonomy data)
```

---

## Testing Commands

Use the following commands to verify fixes:

```bash
# Test all commands with CSV output
uv run misp-cli roles list --csv
uv run misp-cli attribute-blocklists list --csv
uv run misp-cli decaying-models list --csv
uv run misp-cli logs list --csv --limit 2
uv run misp-cli news list --csv
uv run misp-cli warninglists list --csv

# Verify -o option is removed (should show error)
uv run misp-cli -o csv events list
```

---

## Related Files

- `src/misp_cli/cli/app.py` - Main app (removed `-o` option)
- `src/misp_cli/cli/commands/roles.py` - Roles command
- `src/misp_cli/cli/commands/attribute_blocklists.py` - Attribute blocklists
- `src/misp_cli/cli/commands/decaying_models.py` - Decaying models
- `src/misp_cli/cli/commands/logs.py` - Logs command
- `src/misp_cli/cli/commands/news.py` - News command
- `src/misp_cli/cli/commands/warninglists.py` - Warninglists command
- `src/misp_cli/cli/commands/noticelists.py` - Reference implementation with `_unwrap_nested_data()`
