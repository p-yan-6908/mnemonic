from typing import List, Dict, Optional
from mnemonic.strategies.base import Strategy
from mnemonic.strategies.recency import RecencyStrategy
from mnemonic.strategies.importance import ImportanceStrategy
from mnemonic.strategies.semantic import SemanticRetrievalStrategy


class HybridStrategy:
    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        strategies: Optional[Dict[str, Strategy]] = None,
    ):
        self._weights = weights or {
            "recency": 0.4,
            "importance": 0.3,
            "semantic": 0.3,
        }

        self._strategies = strategies or {
            "recency": RecencyStrategy(),
            "importance": ImportanceStrategy(),
            "semantic": SemanticRetrievalStrategy(),
        }

        total = sum(self._weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")

    @property
    def name(self) -> str:
        return "hybrid"

    def score(self, message, context: List) -> float:
        total_score = 0.0

        for strategy_name, weight in self._weights.items():
            strategy = self._strategies.get(strategy_name)
            if strategy:
                try:
                    score = strategy.score(message, context)
                    total_score += weight * score
                except Exception:
                    pass

        return total_score

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

    def set_weight(self, strategy_name: str, weight: float) -> None:
        old_weights = self._weights.copy()
        self._weights[strategy_name] = weight

        total = sum(self._weights.values())
        if abs(total - 1.0) > 0.01:
            self._weights = old_weights
            raise ValueError(f"Weights must sum to 1.0, got {total}")

    def get_weights(self) -> Dict[str, float]:
        return self._weights.copy()
