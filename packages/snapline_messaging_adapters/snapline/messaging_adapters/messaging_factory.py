from __future__ import annotations

from typing import Any

from .memory.memory_queue import create_in_memory_messaging
from .types import MessageConsumerLike, MessagePublisherLike


class _MessagingFactory:
    def memory(self, queue_id: str = "default") -> dict[str, Any]:
        return create_in_memory_messaging(queue_id)

    def custom_publisher(self, publisher: MessagePublisherLike) -> MessagePublisherLike:
        return publisher

    def custom_consumer(self, consumer: MessageConsumerLike) -> MessageConsumerLike:
        return consumer


messaging = _MessagingFactory()
