from typing import List, Optional, Dict, Any, Protocol
import numpy as np
from datetime import datetime

from mnemonic.core.models import MemoryItem


class VectorStore(Protocol):
    def add(self, items: List[MemoryItem], embeddings: np.ndarray) -> None:
        raise NotImplementedError

    def search(self, query_embedding: np.ndarray, top_k: int) -> List[tuple]:
        raise NotImplementedError

    def delete(self, item_ids: List[str]) -> None:
        raise NotImplementedError


class InMemoryVectorStore:
    def __init__(self):
        self._items: Dict[str, MemoryItem] = {}
        self._embeddings: Dict[str, np.ndarray] = {}

    def add(self, items: List[MemoryItem], embeddings: np.ndarray) -> None:
        for i, item in enumerate(items):
            self._items[item.id] = item
            self._embeddings[item.id] = embeddings[i]

    def search(self, query_embedding: np.ndarray, top_k: int = 10) -> List[tuple]:
        if not self._embeddings:
            return []

        similarities = []
        for item_id, emb in self._embeddings.items():
            sim = self._cosine_similarity(query_embedding, emb)
            similarities.append((item_id, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def delete(self, item_ids: List[str]) -> None:
        for item_id in item_ids:
            self._items.pop(item_id, None)
            self._embeddings.pop(item_id, None)

    def get_item(self, item_id: str) -> Optional[MemoryItem]:
        return self._items.get(item_id)

    def clear(self) -> None:
        self._items.clear()
        self._embeddings.clear()


class SemanticSearchMixin:
    def __init__(self):
        self._vector_store = InMemoryVectorStore()

    def semantic_search(
        self,
        query: str,
        top_k: int = 10,
    ) -> List[MemoryItem]:
        query_emb = self._get_embedding(query)

        results = self._vector_store.search(query_emb, top_k)

        items = []
        for item_id, score in results:
            item = self._vector_store.get_item(item_id)
            if item:
                items.append(item)

        return items

    def _get_embedding(self, text: str) -> np.ndarray:
        import hashlib

        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        arr = np.frombuffer(hash_bytes[:32], dtype=np.uint8)
        return arr.astype(np.float32) / 255.0

    def index_messages(self, messages: List[MemoryItem]) -> None:
        if not messages:
            return

        contents = [m.message.content for m in messages]
        embeddings = np.array([self._get_embedding(c) for c in contents])

        self._vector_store.add(messages, embeddings)
