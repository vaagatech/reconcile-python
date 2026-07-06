#!/usr/bin/env python3
"""Run the full 19-scenario integration demo."""
from __future__ import annotations

import asyncio
import importlib.util
import sys
from pathlib import Path


def main() -> int:
    path = Path(__file__).parent / "demo" / "run_all" / "run_all.py"
    spec = importlib.util.spec_from_file_location("snapline_run_all", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return asyncio.run(module.main())


if __name__ == "__main__":
    sys.exit(main())
