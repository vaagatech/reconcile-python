from __future__ import annotations

import json
from typing import Any

from .types import TestRunReport


def _format_diff(diff: Any) -> str:
    if not diff:
        return "none"
    return json.dumps(diff, indent=2).replace("\n", "\n      ")


def render_text_report(report: TestRunReport) -> str:
    lines = [
        "snapline-engine — Test Run Report",
        "=====================================",
        f"Generated: {report['generatedAt']}",
        f"Duration:  {report['summary'].get('durationMs') or 0}ms",
        "",
        f"Total:  {report['summary']['total']}",
        f"Passed: {report['summary']['passed']}",
        f"Failed: {report['summary']['failed']}",
        "",
    ]

    for suite in report["suites"]:
        lines.append(f"{'PASS' if suite['passed'] else 'FAIL'}  {suite['name']}")
        for step in suite["results"]:
            lines.append(f"  {'✓' if step['passed'] else '✗'} {step['step']}")
            if not step["passed"] and step.get("message"):
                lines.append(f"      message: {step['message']}")
            if not step["passed"] and step.get("diff"):
                lines.append(f"      diff:\n      {_format_diff(step['diff'])}")
        lines.append("")

    return "\n".join(lines) + "\n"
