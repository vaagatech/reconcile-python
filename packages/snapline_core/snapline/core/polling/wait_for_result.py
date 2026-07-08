from __future__ import annotations

import asyncio
import time
from typing import Any, Awaitable, Callable


async def wait_for_result(
    check: Callable[[], Awaitable[Any | None]],
    *,
    timeout_ms: int = 30_000,
    interval_ms: int = 250,
) -> Any:
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        result = await check()
        if result is not None:
            return result
        await asyncio.sleep(interval_ms / 1000)
    raise TimeoutError(f"Timed out after {timeout_ms}ms waiting for async result")
