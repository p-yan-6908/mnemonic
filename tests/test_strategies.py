import pytest
from datetime import datetime
from mnemonic.core.models import MemoryItem, Message
from mnemonic.strategies.recency import RecencyStrategy
from mnemonic.strategies.importance import ImportanceStrategy
from mnemonic.strategies.semantic import SemanticRetrievalStrategy
from mnemonic.strategies.hybrid import HybridStrategy
from mnemonic.core.token_tracker import TokenTracker


class TestRecencyStrategy:
    def test_score_favors_recent_messages(self):
        strategy = RecencyStrategy()

        older = MemoryItem(
            id="1",
            message=Message(role="user", content="old", timestamp=datetime(2024, 1, 1)),
        )
        newer = MemoryItem(
            id="2",
            message=Message(role="user", content="new", timestamp=datetime(2024, 1, 2)),
        )

        context = [older, newer]

        older_score = strategy.score(older, context)
        newer_score = strategy.score(newer, context)

        assert older_score < newer_score
        assert newer_score == 1.0

    def test_select_respects_token_limit(self):
        strategy = RecencyStrategy()
        tracker = TokenTracker(max_tokens=10000)

        messages = [
            MemoryItem(
                id=f"{i}",
                message=Message(
                    role="user",
                    content=f"message {i} " * 20,
                    timestamp=datetime(2024, 1, i + 1),
                    token_count=5,
                ),
            )
            for i in range(10)
        ]

        selected = strategy.select(messages, 20, tracker)

        total_tokens = sum(m.message.token_count or 5 for m in selected)
        assert total_tokens <= 20

    def test_select_returns_newest_first(self):
        strategy = RecencyStrategy()
        tracker = TokenTracker(max_tokens=10000)

        messages = [
            MemoryItem(
                id=f"{i}",
                message=Message(
                    role="user",
                    content=f"message {i}",
                    timestamp=datetime(2024, 1, i + 1),
                    token_count=1,
                ),
            )
            for i in range(5)
        ]

        selected = strategy.select(messages, 10, tracker)

        timestamps = [m.message.timestamp for m in selected]
        assert timestamps == sorted(timestamps)

    def test_name_is_recency(self):
        strategy = RecencyStrategy()
        assert strategy.name == "recency"


class TestImportanceStrategy:
    def test_importance_keywords_boost_score(self):
        strategy = ImportanceStrategy()

        normal_msg = MemoryItem(
            id="1",
            message=Message(role="user", content="hello"),
        )
        important_msg = MemoryItem(
            id="2",
            message=Message(role="user", content="remember to fix the critical bug"),
        )

        normal_score = strategy.score(normal_msg, [normal_msg])
        important_score = strategy.score(important_msg, [important_msg])

        assert important_score > normal_score

    def test_assistant_role_boosts_score(self):
        strategy = ImportanceStrategy()

        user_msg = MemoryItem(
            id="1",
            message=Message(role="user", content="hello"),
        )
        assistant_msg = MemoryItem(
            id="2",
            message=Message(role="assistant", content="hello"),
        )

        user_score = strategy.score(user_msg, [user_msg, assistant_msg])
        assistant_score = strategy.score(assistant_msg, [user_msg, assistant_msg])

        assert assistant_score > user_score

    def test_select_respects_token_limit(self):
        strategy = ImportanceStrategy()

        messages = [
            MemoryItem(
                id=f"{i}",
                message=Message(
                    role="user",
                    content=f"message {i} " * 20,
                    timestamp=datetime(2024, 1, i + 1),
                    token_count=5,
                ),
            )
            for i in range(10)
        ]

        class MockTracker:
            def count_tokens(self, text):
                return 5

        selected = strategy.select(messages, 15, MockTracker())

        total_tokens = sum(m.message.token_count or 5 for m in selected)
        assert total_tokens <= 15

    def test_name_is_importance(self):
        strategy = ImportanceStrategy()
        assert strategy.name == "importance"


class TestSemanticRetrievalStrategy:
    def test_select_returns_messages(self):
        strategy = SemanticRetrievalStrategy()

        messages = [
            MemoryItem(
                id=f"{i}",
                message=Message(
                    role="user",
                    content=f"message {i}",
                    timestamp=datetime(2024, 1, i + 1),
                    token_count=1,
                ),
            )
            for i in range(5)
        ]

        class MockTracker:
            def count_tokens(self, text):
                return 1

        selected = strategy.select(messages, 10, MockTracker())

        assert len(selected) > 0

    def test_name_is_semantic(self):
        strategy = SemanticRetrievalStrategy()
        assert strategy.name == "semantic"


class TestHybridStrategy:
    def test_default_weights_sum_to_one(self):
        strategy = HybridStrategy()

        weights = strategy.get_weights()
        total = sum(weights.values())

        assert abs(total - 1.0) < 0.01

    def test_custom_weights(self):
        strategy = HybridStrategy(
            weights={
                "recency": 0.5,
                "importance": 0.3,
                "semantic": 0.2,
            }
        )

        weights = strategy.get_weights()

        assert weights["recency"] == 0.5
        assert weights["importance"] == 0.3
        assert weights["semantic"] == 0.2

    def test_invalid_weights_raises(self):
        with pytest.raises(ValueError):
            HybridStrategy(weights={"recency": 0.5, "importance": 0.3})

    def test_select_uses_all_strategies(self):
        strategy = HybridStrategy()

        messages = [
            MemoryItem(
                id=f"{i}",
                message=Message(
                    role="user",
                    content=f"important message {i}",
                    timestamp=datetime(2024, 1, i + 1),
                    token_count=2,
                ),
            )
            for i in range(5)
        ]

        class MockTracker:
            def count_tokens(self, text):
                return 2

        selected = strategy.select(messages, 10, MockTracker())

        assert len(selected) > 0

    def test_name_is_hybrid(self):
        strategy = HybridStrategy()
        assert strategy.name == "hybrid"
