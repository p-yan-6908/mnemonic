import pytest
from mnemonic.core.token_tracker import TokenTracker


class TestTokenTracker:
    def test_initial_count_is_zero(self):
        tracker = TokenTracker(max_tokens=1000)
        assert tracker.count == 0

    def test_add_tokens_increments_count(self):
        tracker = TokenTracker(max_tokens=1000)
        tokens = tracker.add_tokens("hello world")
        assert tracker.count > 0

    def test_remove_tokens_decrements_count(self):
        tracker = TokenTracker(max_tokens=1000)
        tracker.add_tokens("hello world")
        initial = tracker.count
        tracker.remove_tokens(2)
        assert tracker.count < initial

    def test_warning_threshold_fires(self):
        tracker = TokenTracker(max_tokens=100, warning_threshold=0.5)
        warning_fired = []
        tracker.on_warning(lambda: warning_fired.append(True))

        tracker.add_tokens("x " * 60)

        assert tracker.is_warning()

    def test_critical_threshold_fires(self):
        tracker = TokenTracker(max_tokens=100, critical_threshold=0.9)

        tracker.add_tokens("x " * 95)

        assert tracker.is_critical()

    def test_reset_clears_count(self):
        tracker = TokenTracker(max_tokens=1000)
        tracker.add_tokens("hello world")
        tracker.reset()

        assert tracker.count == 0

    def test_usage_ratio_calculation(self):
        tracker = TokenTracker(max_tokens=1000)
        tracker.add_tokens("hello")

        assert 0 < tracker.usage_ratio < 1

    def test_add_message_formats_correctly(self):
        tracker = TokenTracker(max_tokens=10000)
        tokens = tracker.add_message("user", "Hello")

        assert tokens > 0
        assert tracker.count > 0
