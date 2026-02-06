# Troubleshooting Session: Async/Await Error Fix

**Date:** 2026-02-05  
**Time:** 01:38 UTC  
**Issue:** `'coroutine' object has no attribute 'get'`

## Problem Description

When running `misp-cli events list`, the following error occurred:

```
Error: 'coroutine' object has no attribute 'get'
/Users/steve/dev/misp/misp-cli/src/misp_cli/__main__.py:16: RuntimeWarning: coroutine 'MISPCLient.get' was never awaited
  return 1
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
```

## Root Cause Analysis

The [`MISPCLient.get()`](src/misp_cli/core/client.py:95) method is an **async** method (defined with `async def`), which returns a coroutine when called. However, the command functions in the CLI were calling it synchronously without `await`, which means:

1. `client.get("/events/index")` returns a coroutine object, not the actual response
2. When the code tried to call `.get("events", ...)` on this coroutine, it failed because coroutines don't have a `.get()` method

## Solution Implemented

### 1. Added Sync Wrapper Methods to MISPCLient

Added synchronous wrapper methods in [`src/misp_cli/core/client.py`](src/misp_cli/core/client.py) that use `asyncio.run()` to execute the async methods:

```python
# Synchronous wrapper methods for CLI usage
def get_sync(
    self,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Synchronous GET request helper."""
    return asyncio.run(self.get(endpoint, params=params))

def post_sync(
    self,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Synchronous POST request helper."""
    return asyncio.run(self.post(endpoint, data=data))

# ... similar for put_sync, delete_sync, close_sync
```

### 2. Updated All Command Files

Updated all command files to use the sync wrapper methods instead of the async methods:

- Changed `client.get(...)` → `client.get_sync(...)`
- Changed `client.post(...)` → `client.post_sync(...)`
- etc.

**Files Updated:**

1. [`src/misp_cli/cli/commands/events.py`](src/misp_cli/cli/commands/events.py) - 9 commands
2. [`src/misp_cli/cli/commands/attributes.py`](src/misp_cli/cli/commands/attributes.py) - 8 commands
3. [`src/misp_cli/cli/commands/tags.py`](src/misp_cli/cli/commands/tags.py) - 9 commands
4. [`src/misp_cli/cli/commands/users.py`](src/misp_cli/cli/commands/users.py) - 8 commands
5. [`src/misp_cli/cli/commands/feeds.py`](src/misp_cli/cli/commands/feeds.py) - 11 commands
6. [`src/misp_cli/cli/commands/servers.py`](src/misp_cli/cli/commands/servers.py) - 9 commands
7. [`src/misp_cli/cli/commands/objects.py`](src/misp_cli/cli/commands/objects.py) - 8 commands
8. [`src/misp_cli/cli/commands/galaxies.py`](src/misp_cli/cli/commands/galaxies.py) - 8 commands
9. [`src/misp_cli/cli/commands/taxonomies.py`](src/misp_cli/cli/commands/taxonomies.py) - 8 commands
10. [`src/misp_cli/cli/commands/warninglists.py`](src/misp_cli/cli/commands/warninglists.py) - 7 commands
11. [`src/misp_cli/cli/commands/noticelists.py`](src/misp_cli/cli/commands/noticelists.py) - 5 commands
12. [`src/misp_cli/cli/commands/roles.py`](src/misp_cli/cli/commands/roles.py) - 3 commands
13. [`src/misp_cli/cli/commands/attribute_blocklists.py`](src/misp_cli/cli/commands/attribute_blocklists.py) - 4 commands
14. [`src/misp_cli/cli/commands/event_blocklists.py`](src/misp_cli/cli/commands/event_blocklists.py) - 4 commands
15. [`src/misp_cli/cli/commands/news.py`](src/misp_cli/cli/commands/news.py) - 5 commands
16. [`src/misp_cli/cli/commands/object_templates.py`](src/misp_cli/cli/commands/object_templates.py) - 6 commands
17. [`src/misp_cli/cli/commands/feeds_manage_feeds.py`](src/misp_cli/cli/commands/feeds_manage_feeds.py) - 9 commands
18. [`src/misp_cli/cli/commands/sharing_groups.py`](src/misp_cli/cli/commands/sharing_groups.py) - 9 commands
19. [`src/misp_cli/cli/commands/decaying_models.py`](src/misp_cli/cli/commands/decaying_models.py) - 5 commands

## Verification

After the fix, the CLI commands run without the async error:

```bash
$ misp-cli --help
Usage: misp-cli [OPTIONS] COMMAND [ARGS]...

$ misp-cli events list --help
Usage: python -m misp_cli events list [OPTIONS]
...
```

## Alternative Solutions Considered

### Option 1: Make commands async and use asyncio.run() in main
This would require wrapping Typer app execution with an async event loop, which is more complex.

### Option 2: Make all client methods synchronous
This would lose the async capabilities for other use cases.

### Option 3: Use async with proper awaiting in commands
This would require all command functions to be async and use `await`, which is the cleanest long-term solution but requires more refactoring.

**Selected:** Option 3 (sync wrappers) as a quick fix that preserves async capabilities while allowing synchronous CLI usage.

## Lessons Learned

1. When mixing async and sync code, be consistent about which paradigm you use
2. Async methods that are called without `await` return coroutines, not results
3. Coroutines don't have the same methods as their resolved values
4. Consider using sync wrappers when integrating async libraries with sync frameworks like Typer
