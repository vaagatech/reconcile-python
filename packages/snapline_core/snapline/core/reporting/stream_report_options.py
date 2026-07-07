from __future__ import annotations

from typing import TypedDict


class StreamReportOptions(TypedDict, total=False):
    outputPath: str
    redactFields: list[str]
