from __future__ import annotations

from typing import Any, TypedDict

from snapline.engine.types import DataMappingMap, TransformationMap

from ..reporting.stream_report_options import StreamReportOptions


class WarehouseTableSpec(TypedDict, total=False):
    id: str
    sourceQuery: str
    sourceParams: dict[str, Any]
    sourceCollection: str
    sourceFilter: dict[str, Any]
    targetQuery: str
    targetParams: dict[str, Any]
    targetCollection: str
    linkKeys: dict[str, str]
    ignoreFields: list[str]
    transformations: TransformationMap
    dataMapping: DataMappingMap


class WarehouseStreamReportOptions(StreamReportOptions, total=False):
    format: str


class RunWarehouseComparisonOptions(TypedDict, total=False):
    suiteName: str
    sourceDb: Any
    targetDb: Any
    tables: list[WarehouseTableSpec]
    chunkSize: int
    maxRowsPerTable: int
    maxTotalRows: int
    report: WarehouseStreamReportOptions
