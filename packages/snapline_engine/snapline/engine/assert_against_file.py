from __future__ import annotations

from pathlib import Path
from typing import Any

from .io.load_json_file import load_json_file
from .snapline import snapline
from .types import SnaplineOptions


def assert_against_file(
    live_data: Any,
    expected_file_path: str | Path,
    options: SnaplineOptions | dict[str, Any] | None = None,
) -> dict[str, Any]:
    expected_data = load_json_file(expected_file_path)
    return snapline(live_data, expected_data, options)
