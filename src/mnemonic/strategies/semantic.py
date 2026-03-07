from typing import List, Optional
import numpy as np


class SemanticRetrievalStrategy:
    def __init__(
        self,
        embedding_provider=None,
        top_k: int = 10,
    ):
        self._embedding = embedding_provider
        self._top_k = top_k

    @property
    def name(self) -> str:
        return "semantic"

    def score(self, message, context: List) -> float:
        return 0.5

    def select(
        self,
        messages: List,
        target_tokens: int,
        token_counter,
    ) -> List:
        if not messages:
            return []

        if len(messages) <= 3:
            return messages

        scores = self._compute_relevance_scores(messages)

        indexed = list(zip(messages, scores))
        indexed.sort(key=lambda x: x[1], reverse=True)

        selected = []
        current_tokens = 0

        for msg, score in indexed:
            tokens = msg.message.token_count or token_counter.count_tokens(
                msg.message.content
            )

            if current_tokens + tokens <= target_tokens:
                selected.append(msg)
                current_tokens += tokens

            if len(selected) >= self._top_k:
                break

        selected.sort(key=lambda m: m.message.timestamp)
        return selected

    def _compute_relevance_scores(self, messages: List) -> List[float]:
        if not self._embedding:
            return self._default_scoring(messages)

        try:
            contents = [m.message.content for m in messages]
            embeddings = self._embedding.encode(contents)

            n = len(messages)
            scores = []

            for i in range(n):
                current_emb = embeddings[i]

                future_embs = embeddings[i + 1 :] if i + 1 < n else []

                if len(future_embs) > 0:
                    future_mean = np.mean(future_embs, axis=0)
                    similarity = self._cosine_similarity(current_emb, future_mean)
                    forward_score = (similarity + 1) / 2
                else:
                    forward_score = 0.8

                recency_factor = i / max(n - 1, 1)

                score = 0.6 * forward_score + 0.4 * (1 - recency_factor)
                scores.append(score)

            return scores

        except Exception:
            return self._default_scoring(messages)

    def _default_scoring(self, messages: List) -> List[float]:
        n = len(messages)
        scores = []
        for i in range(n):
            recency = i / max(n - 1, 1)
            position_in_convo = (n - i) / n
            scores.append(0.5 * (1 - recency) + 0.5 * position_in_convo)
        return scores

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
