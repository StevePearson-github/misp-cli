# Troubleshooting Session: Attributes Categories Command Fix

**Date:** 2026-02-05  
**Time:** 02:18 UTC  
**Issue:** `misp-cli attributes categories` throws "Not Found" error

## Problem Description

When running `misp-cli attributes categories`, the following error occurred:

```
Error: Not Found: Resource '/attributes/describeCategories' not found
```

## Root Cause Analysis

The [`list_attribute_categories()`](src/misp_cli/cli/commands/attributes.py:273) function was calling the `/attributes/describeCategories` endpoint, which doesn't exist in the MISP API.

Investigation revealed that:
1. The MISP API doesn't have a dedicated `/attributes/describeCategories` endpoint
2. The `/attributes/describeTypes` endpoint returns both types and categories in its response structure
3. The categories are available in `response["result"]["categories"]`

## Solution Implemented

Updated [`src/misp_cli/cli/commands/attributes.py`](src/misp_cli/cli/commands/attributes.py:273) to:

1. Call `/attributes/describeTypes` instead of `/attributes/describeCategories`
2. Extract categories from `response.get("result", {}).get("categories", [])`

**Code change:**

```python
@attributes_app.command("categories")
def list_attribute_categories(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List all available attribute categories."""
    config = MISPConfig.from_file()
    client = MISPCLient(
        base_url=config.url,
        api_key=config.api_key,
        verify_ssl=config.verify_ssl,
    )
    
    # Get types which includes category information
    response = client.get_sync("/attributes/describeTypes")
    result = response.get("result", {})
    categories = result.get("categories", [])
    
    if config.output_format == "json" or json_output:
        _print_json(categories)
    else:
        typer.echo("Available attribute categories:")
        for c in categories:
            typer.echo(f"  - {c}")
```

## Verification

After the fix, the command successfully lists all 16 attribute categories:

```bash
$ misp-cli attributes categories
[
    "Internal reference",
    "Targeting data",
    "Antivirus detection",
    "Payload delivery",
    "Artifacts dropped",
    "Payload installation",
    "Persistence mechanism",
    "Network activity",
    "Payload type",
    "Attribution",
    "External analysis",
    "Financial fraud",
    "Support Tool",
    "Social network",
    "Person",
    "Other"
]
```

## Lessons Learned

1. MISP API endpoints may not exist as expected - always verify against actual API responses
2. The `/attributes/describeTypes` endpoint returns a comprehensive response including types, categories, and type-to-category mappings
3. When an endpoint doesn't exist, check for parent or sibling endpoints that may contain the needed data
