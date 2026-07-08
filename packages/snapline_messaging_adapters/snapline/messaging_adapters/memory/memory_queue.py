from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

from ..types import (
    MessageConsumerLike,
    MessagePublishInput,
    MessagePublishResult,
    MessagePublisherLike,
    MessageReceived,
    MessageWaitOptions,
)

_brokers: dict[str, dict[str, list[dict[str, Any]]]] = {}


def _broker_for(queue_id: str) -> dict[str, list[dict[str, Any]]]:
    if queue_id not in _brokers:
        _brokers[queue_id] = {}
    return _brokers[queue_id]


class InMemoryMessagePublisher:
    def __init__(self, queue_id: str = "default") -> None:
        self._queue_id = queue_id

    async def publish(self, topic: str, message: MessagePublishInput) -> MessagePublishResult:
        correlation_id = message.get("correlationId") or str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        headers = {**(message.get("headers") or {}), "x-correlation-id": correlation_id}

        entry = {
            "topic": topic,
            "payload": message.get("payload"),
            "headers": headers,
            "correlationId": correlation_id,
            "messageId": message_id,
            "createdAt": time.time(),
        }

        topics = _broker_for(self._queue_id)
        topics.setdefault(topic, []).append(entry)
        return {"correlationId": correlation_id, "messageId": message_id, "topic": topic}


class InMemoryMessageConsumer:
    def __init__(self, queue_id: str = "default") -> None:
        self._queue_id = queue_id

    async def wait_for_message(
        self, topic: str, options: MessageWaitOptions | None = None
    ) -> MessageReceived:
        opts = options or {}
        timeout_ms = opts.get("timeoutMs", 30_000)
        deadline = time.monotonic() + timeout_ms / 1000

        while time.monotonic() < deadline:
            topics = _broker_for(self._queue_id)
            queue = topics.get(topic, [])
            for index, msg in enumerate(queue):
                if opts.get("correlationId") and msg["correlationId"] != opts["correlationId"]:
                    continue
                queue.pop(index)
                return {
                    "topic": msg["topic"],
                    "payload": msg["payload"],
                    "headers": msg["headers"],
                    "correlationId": msg["correlationId"],
                    "messageId": msg["messageId"],
                }
            await asyncio.sleep(0.05)

        suffix = f" (correlationId={opts['correlationId']})" if opts.get("correlationId") else ""
        raise TimeoutError(
            f"Timed out after {timeout_ms}ms waiting for message on topic '{topic}'{suffix}"
        )


def reset_in_memory_brokers() -> None:
    _brokers.clear()


def create_in_memory_messaging(queue_id: str = "default") -> dict[str, Any]:
    return {
        "publisher": InMemoryMessagePublisher(queue_id),
        "consumer": InMemoryMessageConsumer(queue_id),
    }
