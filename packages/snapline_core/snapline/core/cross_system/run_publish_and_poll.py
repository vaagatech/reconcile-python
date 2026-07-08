from __future__ import annotations

import uuid
from typing import Any

from snapline.engine import assert_against_file, snapline

from ..polling.create_resolvers import (
    create_db_async_result_resolver,
    create_file_async_result_resolver,
    create_message_async_result_resolver,
)


async def _resolve_poll_target(poll: dict[str, Any]):
    if "resolver" in poll:
        return poll["resolver"]
    if "db" in poll:
        return create_db_async_result_resolver(poll["db"])
    if "file" in poll:
        return create_file_async_result_resolver(poll["file"])
    return create_message_async_result_resolver(poll["message"])


async def run_publish_and_poll(config: dict[str, Any]) -> dict[str, Any]:
    publish = config["publish"]
    poll_options = config.get("pollOptions") or {}
    expected_file = config.get("expectedFile")
    expected = config.get("expected")
    ignore_fields = config.get("ignoreFields", [])
    transformations = config.get("transformations", {})
    data_mapping = config.get("dataMapping", {})

    correlation_id = publish.get("correlationId") or str(uuid.uuid4())
    await publish["publisher"].publish(
        publish["topic"],
        {
            "payload": publish["payload"],
            "headers": publish.get("headers"),
            "correlationId": correlation_id,
            "key": publish.get("key"),
        },
    )

    resolver = await _resolve_poll_target(config["poll"])
    actual = await resolver.wait_for_result(correlation_id, poll_options)

    if expected_file:
        assertion = assert_against_file(
            actual,
            expected_file,
            {
                "ignoreFields": ignore_fields,
                "transformations": transformations,
                "dataMapping": data_mapping,
            },
        )
        return {
            "match": assertion["match"],
            "source": assertion["processed"],
            "target": assertion["expected"],
            "diff": assertion["diff"],
        }

    result = snapline(
        actual,
        expected,
        {
            "ignoreFields": ignore_fields,
            "transformations": transformations,
            "dataMapping": data_mapping,
        },
    )
    return {
        "match": result["match"],
        "source": result["processed"],
        "target": result["expected"],
        "diff": result["diff"],
    }
