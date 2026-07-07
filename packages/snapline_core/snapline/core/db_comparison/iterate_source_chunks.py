from __future__ import annotations

import re
from typing import Any, AsyncIterator, Optional


async def iterate_source_chunks(
    source_db: Any,
    base_query: str,
    params: dict[str, Any],
    *,
    chunk_size: int,
    max_rows: Optional[int] = None,
) -> AsyncIterator[list[dict[str, Any]]]:
    size = max(1, chunk_size)
    offset = 0
    total_fetched = 0

    while True:
        if max_rows is not None and total_fetched >= max_rows:
            return

        remaining = size if max_rows is None else min(size, max_rows - total_fetched)
        paginated = base_query if re.search(r"\blimit\s+\d+", base_query, re.I) else (
            f"{base_query.strip()} LIMIT {remaining} OFFSET {offset}"
        )

        rows = source_db.query(paginated, params)
        if hasattr(rows, "__await__"):
            rows = await rows

        if not rows:
            return

        yield rows
        total_fetched += len(rows)
        offset += len(rows)
        if len(rows) < remaining:
            return
