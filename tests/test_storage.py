import pytest
from mnemonic.storage.memory import InMemoryStorage
from mnemonic.core.models import MemoryItem, Message, Session


class TestInMemoryStorage:
    def test_add_and_get_item(self):
        storage = InMemoryStorage()
        item = MemoryItem(id="test1", message=Message(role="user", content="hello"))

        storage.add(item)
        retrieved = storage.get("test1")

        assert retrieved is not None
        assert retrieved.id == "test1"

    def test_list_returns_session_messages(self):
        storage = InMemoryStorage()
        session = Session(id="sess1")

        for i in range(5):
            item = MemoryItem(
                id=f"sess1_{i}",
                message=Message(role="user", content=f"message {i}"),
            )
            storage.add(item)

        items = storage.list("sess1", limit=3)

        assert len(items) == 3

    def test_delete_removes_item(self):
        storage = InMemoryStorage()
        item = MemoryItem(id="test1", message=Message(role="user", content="hello"))

        storage.add(item)
        result = storage.delete("test1")

        assert result is True
        assert storage.get("test1") is None

    def test_update_modifies_item(self):
        storage = InMemoryStorage()
        item = MemoryItem(id="test1", message=Message(role="user", content="hello"))

        storage.add(item)
        item.importance_score = 0.9
        storage.update(item)

        retrieved = storage.get("test1")
        assert retrieved.importance_score == 0.9

    def test_save_and_get_session(self):
        storage = InMemoryStorage()
        session = Session(id="sess1")

        storage.save_session(session)
        retrieved = storage.get_session("sess1")

        assert retrieved is not None
        assert retrieved.id == "sess1"

    def test_list_sessions_returns_sorted_sessions(self):
        storage = InMemoryStorage()

        session1 = Session(id="sess1")
        session2 = Session(id="sess2")

        storage.save_session(session1)
        storage.save_session(session2)

        sessions = storage.list_sessions(limit=10)

        assert len(sessions) == 2

    def test_clear_removes_all(self):
        storage = InMemoryStorage()
        item = MemoryItem(id="test1", message=Message(role="user", content="hello"))

        storage.add(item)
        storage.clear()

        assert len(storage.list("sess1")) == 0
