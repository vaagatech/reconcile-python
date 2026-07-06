from __future__ import annotations

from snapline.engine import reconcile

from ..types import CrossSystemResult, DbComparisonConfig
from .fetch_store_data import fetch_source_row, fetch_target_row


async def run_db_comparison(db_comparison: DbComparisonConfig | dict) -> CrossSystemResult:
    source_data = await fetch_source_row(db_comparison)
    target_data = await fetch_target_row(db_comparison, source_data)

    result = reconcile(
        source_data,
        target_data,
        {
            "ignoreFields": db_comparison.get("ignoreFields", []),
            "transformations": db_comparison.get("transformations", {}),
            "dataMapping": db_comparison.get("dataMapping", {}),
        },
    )

    return {
        "match": result["match"],
        "source": result["processed"],
        "target": result["expected"],
        "diff": result["diff"],
    }
