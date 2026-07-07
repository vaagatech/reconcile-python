from __future__ import annotations

from typing import Any, TypedDict

from snapline.engine.types import DataMappingMap, TransformationMap


class WarehouseTableSpec(TypedDict, total=False):
    id: str
    sourceQuery: str
    sourceParams: dict[str, Any]
    targetCollection: str
    linkKeys: dict[str, str]
    ignoreFields: list[str]
    transformations: TransformationMap
    dataMapping: DataMappingMap


class WarehouseStreamReportOptions(TypedDict, total=False):
    outputPath: str
    format: str
    redactFields: list[str]


class RunWarehouseComparisonOptions(TypedDict, total=False):
    suiteName: str
    sourceDb: Any
    targetDb: Any
    tables: list[WarehouseTableSpec]
    chunkSize: int
    maxRowsPerTable: int
    maxTotalRows: int
    report: WarehouseStreamReportOptions
