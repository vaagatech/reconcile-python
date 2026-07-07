from __future__ import annotations

from pathlib import Path


def assert_within_root(root: str | Path, file_path: str | Path) -> Path:
    resolved_root = Path(root).resolve()
    resolved_path = Path(file_path).resolve()

    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"Path escapes allowed root: {file_path}") from exc

    return resolved_path


def resolve_safe_path(root: str | Path, file_path: str | Path) -> Path:
    return assert_within_root(root, Path(root) / file_path)
