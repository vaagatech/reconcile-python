from __future__ import annotations

from pathlib import Path
from typing import TypedDict


class FixturesDirOptions(TypedDict, total=False):
    relativePath: str


def module_dir(file: str) -> Path:
    return Path(file).resolve().parent


def fixtures_dir(file: str, options: FixturesDirOptions | None = None) -> Path:
    relative_path = (options or {}).get("relativePath", "../fixtures")
    return module_dir(file) / relative_path
