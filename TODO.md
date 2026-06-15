# TODO

## Architecture

### Fix MISPClient event-loop reuse (tracked debt from v0.2.1)

`MISPClient` creates a single `httpx.AsyncClient` at construction time. Every call to
`get_sync()` / `post_sync()` wraps the async method in `asyncio.run()`, which closes the
event loop when it returns — leaving the cached `httpx.AsyncClient` tied to a dead loop.

The workaround applied in `objects.py` (`add_object`) bundles multiple async calls into
a single `asyncio.run(_add(client))` inner function. This works but must be repeated in
any command that needs more than one API call in sequence.

**Proper fix:** in `MISPClient`, create a fresh `httpx.AsyncClient` per `asyncio.run()`
call rather than caching one at construction. Options:
- Create the client inside each `async` method, or
- Accept the client as a context manager and re-enter it per `asyncio.run()` call, or
- Switch `_sync()` wrappers to use `asyncio.get_event_loop().run_until_complete()` with
  a persistent loop instead of `asyncio.run()`.
