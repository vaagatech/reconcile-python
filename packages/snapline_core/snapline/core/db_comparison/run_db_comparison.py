from __future__ import annotations

from snapline.engine import reconcile

from ..types import CrossSystemResult, DbComparisonConfig


async def run_db_comparison(db_comparison: DbComparisonConfig | dict) -> CrossSystemResult:
    source_rows = await db_comparison["sourceDb"].query(
        db_comparison["query"],
        db_comparison.get("params", {}),
    )
    target_rows = await db_comparison["targetDb"].query(
        db_comparison["query"],
        db_comparison.get("params", {}),
    )

    source_data = source_rows[0] if source_rows else None
    target_data = target_rows[0] if target_rows else None

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
