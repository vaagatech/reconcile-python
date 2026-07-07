from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from snapline.engine import reconcile

from ..types import TestStepResult, TestSuiteResult
from .fetch_store_data import is_document_store
from .iterate_source_chunks import iterate_source_chunks
from .warehouse_types import RunWarehouseComparisonOptions, WarehouseTableSpec
from ..reporting.stream_report import create_stream_report_writer


def _target_filter(source_row: dict[str, Any], link_keys: dict[str, str]) -> dict[str, Any]:
    return {target_field: source_row[source_field] for target_field, source_field in link_keys.items()}


async def _compare_row(
    table: WarehouseTableSpec,
    source_row: dict[str, Any],
    target_db: Any,
) -> dict[str, Any]:
    link_keys = table.get("linkKeys") or {}
    filt = _target_filter(source_row, link_keys)
    matches = await target_db.find(table["targetCollection"], filt)
    target_row = matches[0] if matches else None

    if not target_row:
        return {
            "type": "row",
            "tableId": table["id"],
            "rowIndex": 0,
            "passed": False,
            "sourceKey": next(iter(filt.values()), None),
            "message": f"No target document in {table['targetCollection']} for {filt}",
        }

    result = reconcile(
        source_row,
        target_row,
        {
            "ignoreFields": table.get("ignoreFields", []),
            "transformations": table.get("transformations", {}),
            "dataMapping": table.get("dataMapping", {}),
        },
    )

    return {
        "type": "row",
        "tableId": table["id"],
        "rowIndex": 0,
        "passed": result["match"],
        "sourceKey": next(iter(filt.values()), None),
        "diff": result.get("diff"),
    }


async def run_warehouse_comparison(
    options: RunWarehouseComparisonOptions,
) -> TestSuiteResult:
    suite_name = options["suiteName"]
    source_db = options["sourceDb"]
    target_db = options["targetDb"]
    tables = options["tables"]
    chunk_size = int(options.get("chunkSize") or 100)
    max_rows_per_table = options.get("maxRowsPerTable")
    max_total_rows = options.get("maxTotalRows")
    report = options.get("report")

    if not is_document_store(target_db):
        raise ValueError("run_warehouse_comparison requires a document store target")

    writer = (
        create_stream_report_writer(report["outputPath"], report.get("redactFields"))
        if report and report.get("outputPath")
        else None
    )

    results: list[TestStepResult] = []
    suite_passed = True
    rows_compared = 0
    passed_rows = 0
    failed_rows = 0
    remaining_total = max_total_rows

    print(f"\n▶ {suite_name}")
    print(
        f"  chunkSize={chunk_size}"
        + (f" maxRowsPerTable={max_rows_per_table}" if max_rows_per_table else "")
        + (f" maxTotalRows={max_total_rows}" if max_total_rows else "")
    )

    for table in tables:
        table_passed = True
        table_rows = 0
        table_failed = 0
        chunk_index = 0

        table_limit: Optional[int] = max_rows_per_table
        if table_limit is not None and remaining_total is not None:
            table_limit = min(table_limit, remaining_total)

        async for chunk in iterate_source_chunks(
            source_db,
            table["sourceQuery"],
            table.get("sourceParams") or {},
            chunk_size=chunk_size,
            max_rows=table_limit,
        ):
            if remaining_total is not None and remaining_total <= 0:
                break

            if remaining_total is not None and len(chunk) > remaining_total:
                chunk = chunk[:remaining_total]

            chunk_passed = 0
            chunk_failed = 0

            for source_row in chunk:
                row_result = await _compare_row(table, source_row, target_db)
                row_result["rowIndex"] = table_rows
                table_rows += 1
                rows_compared += 1

                if row_result["passed"]:
                    chunk_passed += 1
                    passed_rows += 1
                else:
                    chunk_failed += 1
                    failed_rows += 1
                    table_failed += 1
                    table_passed = False
                    suite_passed = False

                if writer:
                    writer.write(row_result)

            if writer:
                writer.write(
                    {
                        "type": "chunk",
                        "tableId": table["id"],
                        "chunkIndex": chunk_index,
                        "rowCount": len(chunk),
                        "passed": chunk_passed,
                        "failed": chunk_failed,
                        "at": datetime.now(timezone.utc).isoformat(),
                    }
                )

            chunk_index += 1
            if remaining_total is not None:
                remaining_total -= len(chunk)

        results.append(
            TestStepResult(
                step=table["id"],
                passed=table_passed,
                message=(
                    f"Compared {table_rows} rows"
                    if table_passed
                    else f"{table_failed} of {table_rows} rows failed"
                ),
            )
        )
        print(f"  {'✓' if table_passed else '✗'} {table['id']} ({table_rows} rows)")

    summary = {
        "type": "summary",
        "suiteName": suite_name,
        "tables": len(tables),
        "rowsCompared": rows_compared,
        "passed": passed_rows,
        "failed": failed_rows,
        "at": datetime.now(timezone.utc).isoformat(),
    }

    if writer:
        path = writer.finalize(summary)
        print(f"  Stream report: {path}")

    label = "PASSED" if suite_passed else "FAILED"
    print(f"\n{'✅' if suite_passed else '❌'} {suite_name}: {label}\n")

    return TestSuiteResult(name=suite_name, passed=suite_passed, results=results)
