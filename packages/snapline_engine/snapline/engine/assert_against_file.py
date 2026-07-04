from __future__ import annotations

from pathlib import Path
from typing import Any

from .io.load_json_file import load_json_file
from .reconcile import reconcile
from .types import ReconcileOptions


def assert_against_file(
    live_data: Any,
    expected_file_path: str | Path,
    options: ReconcileOptions | dict[str, Any] | None = None,
) -> dict[str, Any]:
    expected_data = load_json_file(expected_file_path)
    return reconcile(live_data, expected_data, options)
