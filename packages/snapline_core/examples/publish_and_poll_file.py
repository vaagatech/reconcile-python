"""Publish to queue, poll filesystem for async JSON result."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from snapline.core import run_publish_and_poll
from snapline.messaging_adapters import messaging


async def main() -> None:
    out_dir = Path(tempfile.mkdtemp(prefix="snapline-results-"))
    queue = messaging.memory()
    publisher = queue["publisher"]
    consumer = queue["consumer"]

    async def worker() -> None:
        request = await consumer.wait_for_message("jobs.submit")
        file_path = out_dir / f"{request['correlationId']}.json"
        file_path.write_text(
            '{"jobId": "JOB-42", "status": "COMPLETE", "output": {"rows": 128}}',
            encoding="utf-8",
        )

    asyncio.create_task(worker())

    result = await run_publish_and_poll(
        {
            "publish": {
                "publisher": publisher,
                "topic": "jobs.submit",
                "payload": {"jobId": "JOB-42"},
            },
            "poll": {"file": {"directory": str(out_dir)}},
            "expected": {
                "jobId": "JOB-42",
                "status": "COMPLETE",
                "output": {"rows": 128},
            },
            "pollOptions": {"timeoutMs": 5000},
        }
    )

    print("PASSED" if result["match"] else "FAILED")


if __name__ == "__main__":
    asyncio.run(main())
