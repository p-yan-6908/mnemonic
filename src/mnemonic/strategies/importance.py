from typing import List, Optional, Callable
import numpy as np


class EmbeddingProvider:
    def __init__(self, provider: str = "numpy", model: str = "simple"):
        self._provider = provider
        self._model = model
        self._cache = {}

    def encode(self, texts: List[str]) -> np.ndarray:
        if self._provider == "numpy":
            return self._simple_encode(texts)
        raise ValueError(f"Unknown provider: {self._provider}")

    def _simple_encode(self, texts: List[str]) -> np.ndarray:
        vectors = []
        for text in texts:
            if text in self._cache:
                vectors.append(self._cache[text])
            else:
                vec = self._hash_vector(text)
                self._cache[text] = vec
                vectors.append(vec)
        return np.array(vectors)

    def _hash_vector(self, text: str) -> np.ndarray:
        import hashlib

        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        arr = np.frombuffer(hash_bytes[:32], dtype=np.uint8)
        vec = arr.astype(np.float32) / 255.0
        return vec


class ImportanceStrategy:
    def __init__(
        self,
        embedding_provider: Optional[EmbeddingProvider] = None,
        importance_keywords: Optional[List[str]] = None,
    ):
        self._embedding = embedding_provider or EmbeddingProvider()
        self._keywords = importance_keywords or [
            "important",
            "critical",
            "must",
            "remember",
            "don't forget",
            "decision",
            "agreed",
            "decided",
            "use",
            "avoid",
            "fix",
            "bug",
            "error",
            "failed",
            "workaround",
            "api",
            "auth",
            "config",
        ]

    @property
    def name(self) -> str:
        return "importance"

    def score(self, message, context: List) -> float:
        content = message.message.content.lower()

        keyword_score = 0.0
        for kw in self._keywords:
            if kw in content:
                keyword_score += 0.15

        role_score = 0.0
        if message.message.role == "assistant":
            role_score += 0.1
        elif message.message.role == "system":
            role_score += 0.2

        length_score = min(len(content.split()) / 100.0, 0.2)

        return min(keyword_score + role_score + length_score, 1.0)

    def select(
        self,
        messages: List,
        target_tokens: int,
        token_counter,
    ) -> List:
        if not messages:
            return []

        scored = []
        for msg in messages:
            score = self.score(msg, messages)
            tokens = msg.message.token_count or token_counter.count_tokens(
                msg.message.content
            )
            scored.append((score, tokens, msg))

        scored.sort(key=lambda x: x[0], reverse=True)

        selected = []
        current_tokens = 0

        for score, tokens, msg in scored:
            if current_tokens + tokens <= target_tokens:
                selected.append(msg)
                current_tokens += tokens

        selected.sort(key=lambda m: m.message.timestamp)
        return selected
