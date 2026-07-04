from __future__ import annotations

import json

from .types import TestRunReport


def render_json_report(report: TestRunReport) -> str:
    return json.dumps(report, indent=2)
