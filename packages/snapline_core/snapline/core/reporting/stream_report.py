from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional, Union

from snapline.core.reporting.redact_fields import redact_fields


class StreamReportWriter:
    def __init__(
        self,
        output_path: Union[str, Path],
        redact_fields_list: Optional[list[str]] = None,
    ) -> None:
        self._path = Path(output_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self._path.open("w", encoding="utf-8")
        self._redact = redact_fields_list or []

    def write(self, event: dict[str, Any]) -> None:
        sanitized = redact_fields(event, self._redact)
        self._file.write(json.dumps(sanitized) + "\n")

    def finalize(self, summary: dict[str, Any]) -> str:
        self.write(summary)
        self._file.close()
        return str(self._path)


def create_stream_report_writer(
    output_path: Union[str, Path],
    redact_fields_list: Optional[list[str]] = None,
) -> StreamReportWriter:
    return StreamReportWriter(output_path, redact_fields_list)
