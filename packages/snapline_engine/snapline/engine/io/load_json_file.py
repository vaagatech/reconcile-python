from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json_file(path: str | Path, *, root_dir: str | Path | None = None) -> Any:
    resolved = Path(path).resolve()
    if root_dir is not None:
        from .safe_path import assert_within_root

        assert_within_root(root_dir, resolved)

    try:
        with open(resolved, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Failed to read JSON file {resolved}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {resolved}") from exc
