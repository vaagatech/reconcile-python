from __future__ import annotations

from typing import Any, AsyncIterator

from ..types import DbRow


async def iterate_source_documents(
    store: Any,
    collection: str,
    filter: dict[str, Any],
    *,
    chunk_size: int,
    max_rows: int | None = None,
) -> AsyncIterator[list[DbRow]]:
    chunk_size = max(1, chunk_size)
    rows = await store.find(collection, filter)
    limited = rows[:max_rows] if max_rows is not None else rows

    for offset in range(0, len(limited), chunk_size):
        yield limited[offset : offset + chunk_size]
