from __future__ import annotations

from typing import Any

from snapline.engine.types import SnaplineOptions

from .types import FixtureCaseDefaults, FixtureCaseMeta, FixtureCasePresetMaps


def _resolve_preset(value: Any, presets: dict[str, Any] | None) -> Any:
    if isinstance(value, str):
        return presets.get(value) if presets else None
    if isinstance(value, dict):
        return value
    return None


def _resolve_snapline_field(
    case_value: Any,
    default_value: Any,
    presets: dict[str, Any] | None,
) -> Any:
    if case_value is not None:
        return _resolve_preset(case_value, presets)
    if default_value is not None:
        return _resolve_preset(default_value, presets)
    return None


def resolve_fixture_snapline_options(
    meta: FixtureCaseMeta,
    defaults: FixtureCaseDefaults | None,
    presets: FixtureCasePresetMaps,
) -> SnaplineOptions:
    return {
        "ignoreFields": meta.get("ignoreFields") or (defaults or {}).get("ignoreFields"),
        "transformations": _resolve_snapline_field(
            meta.get("transformations"),
            (defaults or {}).get("transformations"),
            presets.get("transformations"),
        ),
        "dataMapping": _resolve_snapline_field(
            meta.get("dataMapping"),
            (defaults or {}).get("dataMapping"),
            presets.get("dataMapping"),
        ),
    }
