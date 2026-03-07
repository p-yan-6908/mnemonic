import pytest
from mnemonic import MnemonicMemory
from mnemonic.core.models import Message


class TestMnemonicMemory:
    def test_initialization(self):
        memory = MnemonicMemory(max_tokens=10000)

        assert memory.token_count == 0
        assert memory.message_count == 0

    def test_add_message_increments_count(self):
        memory = MnemonicMemory(max_tokens=10000)

        memory.add_message("user", "Hello world")

        assert memory.token_count > 0

    def test_get_recent_messages(self):
        memory = MnemonicMemory(max_tokens=10000)

        memory.add_message("user", "First")
        memory.add_message("assistant", "Second")
        memory.add_message("user", "Third")

        recent = memory.get_recent_messages(count=2)

        assert len(recent) == 2

    def test_get_context_for_query(self):
        memory = MnemonicMemory(max_tokens=10000)

        memory.add_message("user", "We're using OAuth2")
        memory.add_message("assistant", "Great choice")
        memory.add_message("user", "What about JWT?")

        context = memory.get_context_for("authentication")

        assert "OAuth2" in context or "JWT" in context

    def test_compaction_reduces_messages(self):
        memory = MnemonicMemory(max_tokens=1000)

        for i in range(20):
            memory.add_message("user", f"Message {i} " * 20)

        initial_count = memory.message_count

        result = memory.compact()

        assert result.compacted_count < initial_count

    def test_warning_callback_fires(self):
        memory = MnemonicMemory(
            max_tokens=100,
            warning_threshold=0.5,
        )

        fired = []
        memory.on_warning(lambda: fired.append(True))

        memory.add_message("user", "x " * 60)

        assert memory.is_warning()

    def test_session_id_persists(self):
        memory = MnemonicMemory(max_tokens=10000, session_id="my-session")

        assert memory.session_id == "my-session"

    def test_usage_ratio_tracks_correctly(self):
        memory = MnemonicMemory(max_tokens=1000)

        memory.add_message("user", "hello")

        assert 0 < memory.usage_ratio < 1

    def test_structured_memory_access(self):
        memory = MnemonicMemory(max_tokens=10000)

        structured = memory.get_structured()

        assert structured is not None
        assert hasattr(structured, "entities")
        assert hasattr(structured, "decisions")
