from __future__ import annotations

from typing import Any, Protocol, TypedDict


class MessagePublishInput(TypedDict, total=False):
    payload: Any
    headers: dict[str, str]
    correlationId: str
    key: str


class MessagePublishResult(TypedDict, total=False):
    correlationId: str
    messageId: str
    topic: str


class MessagePublisherLike(Protocol):
    async def publish(self, topic: str, message: MessagePublishInput) -> MessagePublishResult: ...


class MessageReceived(TypedDict, total=False):
    topic: str
    payload: Any
    headers: dict[str, str]
    correlationId: str
    messageId: str


class MessageWaitOptions(TypedDict, total=False):
    correlationId: str
    timeoutMs: int


class MessageConsumerLike(Protocol):
    async def wait_for_message(
        self, topic: str, options: MessageWaitOptions | None = None
    ) -> MessageReceived: ...
