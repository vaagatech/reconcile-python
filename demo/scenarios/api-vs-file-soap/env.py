from __future__ import annotations

import os

from snapline.core import resolve_report_config, write_test_report


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Set {name} (see .env.example)")
    return value


def finalize_run(result: dict, suite_name: str) -> dict:
    report_config = resolve_report_config()
    if report_config:
        write_test_report(
            [result],
            report_config,
            {"environment": {"suite": suite_name, "reportFormat": report_config["format"]}},
        )
    return result
