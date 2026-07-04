from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeAlias

JsonValue: TypeAlias = Any
FieldTransformation: TypeAlias = Callable[[Any, str, dict[str, Any]], Any]
FieldMapping: TypeAlias = dict[str, Any] | Callable[[Any], Any]
TransformationMap: TypeAlias = dict[str, FieldTransformation]
DataMappingMap: TypeAlias = dict[str, FieldMapping]


class DiffResult(dict):
    """path, actual, expected, message."""

    path: str
    actual: Any
    expected: Any
    message: str


class ReconcileOptions(dict):
    ignoreFields: list[str]
    transformations: TransformationMap
    dataMapping: DataMappingMap


class ReconcileResult(dict):
    match: bool
    processed: Any
    expected: Any
    diff: DiffResult | None


class CompareResult(dict):
    match: bool
    diff: DiffResult | None
