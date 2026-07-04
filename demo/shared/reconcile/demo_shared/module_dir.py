from __future__ import annotations

from pathlib import Path


def module_dir(file: str) -> Path:
    return Path(file).resolve().parent


def fixtures_dir(file: str) -> Path:
    return module_dir(file) / "fixtures"
