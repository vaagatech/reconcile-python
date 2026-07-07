from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, AsyncIterator, Optional

from snapline.engine import reconcile

from ..types import TestStepResult, TestSuiteResult
from .fetch_store_data import fetch_target_row, is_document_store
from .iterate_source_chunks import iterate_source_chunks
from .iterate_source_documents import iterate_source_documents
from .warehouse_types import RunWarehouseComparisonOptions, WarehouseTableSpec
from ..reporting.stream_report import create_stream_report_writer


def _assert_table_spec(table: WarehouseTableSpec, source_is_doc: bool, target_is_doc: bool) -> None:
    table_id = table["id"]
    if source_is_doc and not table.get("sourceCollection"):
        raise ValueError(f'Table "{table_id}" requires sourceCollection for a document source store')
    if not source_is_doc and not table.get("sourceQuery"):
        raise ValueError(f'Table "{table_id}" requires sourceQuery for a SQL source store')
    if target_is_doc and not table.get("targetCollection"):
        raise ValueError(f'Table "{table_id}" requires targetCollection for a document target store')
    if not target_is_doc and not table.get("targetQuery"):
        raise ValueError(f'Table "{table_id}" requires targetQuery for a SQL target store')


def _row_comparison_config(
    options: RunWarehouseComparisonOptions,
    table: WarehouseTableSpec,
) -> dict[str, Any]:
    return {
        "sourceDb": options["sourceDb"],
        "targetDb": options["targetDb"],
        "sourceQuery": table.get("sourceQuery"),
        "sourceParams": table.get("sourceParams"),
        "sourceCollection": table.get("sourceCollection"),
        "sourceFilter": table.get("sourceFilter"),
        "targetQuery": table.get("targetQuery"),
        "targetParams": table.get("targetParams"),
        "targetCollection": table.get("targetCollection"),
        "linkKeys": table.get("linkKeys"),
        "ignoreFields": table.get("ignoreFields", []),
        "transformations": table.get("transformations", {}),
        "dataMapping": table.get("dataMapping", {}),
    }


async def _compare_row(
    options: RunWarehouseComparisonOptions,
    table: WarehouseTableSpec,
    source_row: dict[str, Any],
) -> dict[str, Any]:
    config = _row_comparison_config(options, table)
    target_row = await fetch_target_row(config, source_row)
    link_keys = table.get("linkKeys") or {}
    source_key = next((source_row[field] for field in link_keys.values() if field in source_row), None)

    if not target_row:
        return {
            "type": "row",
            "tableId": table["id"],
            "rowIndex": 0,
            "passed": False,
            "sourceKey": source_key,
            "message": f"No target row for source keys {link_keys}",
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
        "sourceKey": source_key,
        "diff": result.get("diff"),
    }


async def _iterate_table_source_rows(
    options: RunWarehouseComparisonOptions,
    table: WarehouseTableSpec,
    table_limit: Optional[int],
    chunk_size: int,
) -> AsyncIterator[list[dict[str, Any]]]:
    source_db = options["sourceDb"]

    if is_document_store(source_db):
        async for chunk in iterate_source_documents(
            source_db,
            table["sourceCollection"],
            table.get("sourceFilter") or {},
            chunk_size=chunk_size,
            max_rows=table_limit,
        ):
            yield chunk
        return

    async for chunk in iterate_source_chunks(
        source_db,
        table["sourceQuery"],
        table.get("sourceParams") or {},
        chunk_size=chunk_size,
        max_rows=table_limit,
    ):
        yield chunk


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

    source_is_doc = is_document_store(source_db)
    target_is_doc = is_document_store(target_db)

    for table in tables:
        _assert_table_spec(table, source_is_doc, target_is_doc)

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
    print(
        f"  source={'document' if source_is_doc else 'sql'} → target={'document' if target_is_doc else 'sql'}"
    )

    for table in tables:
        table_passed = True
        table_rows = 0
        table_failed = 0
        chunk_index = 0

        table_limit: Optional[int] = max_rows_per_table
        if table_limit is not None and remaining_total is not None:
            table_limit = min(table_limit, remaining_total)

        async for chunk in _iterate_table_source_rows(options, table, table_limit, chunk_size):
            if remaining_total is not None and remaining_total <= 0:
                break
            if remaining_total is not None and len(chunk) > remaining_total:
                chunk = chunk[:remaining_total]

            chunk_passed = 0
            chunk_failed = 0

            for source_row in chunk:
                row_result = await _compare_row(options, table, source_row)
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
