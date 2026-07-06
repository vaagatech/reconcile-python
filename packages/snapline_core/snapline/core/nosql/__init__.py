from __future__ import annotations

from .in_memory_document_store import InMemoryDocumentStore
from .types import DbRow, DocumentStoreLike


class _NosqlModule:
    @staticmethod
    def memory() -> InMemoryDocumentStore:
        return InMemoryDocumentStore()

    @staticmethod
    def seed(store: InMemoryDocumentStore, collection: str, documents: list[DbRow]) -> None:
        store.seed(collection, documents)


nosql = _NosqlModule()

__all__ = ["DbRow", "DocumentStoreLike", "InMemoryDocumentStore", "nosql"]
