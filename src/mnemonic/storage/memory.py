from typing import List, Optional, Dict
from datetime import datetime
from mnemonic.core.models import MemoryItem, Session, StructuredMemory
from mnemonic.storage.base import StorageBackend


class InMemoryStorage:
    def __init__(self):
        self._items: Dict[str, MemoryItem] = {}
        self._sessions: Dict[str, Session] = {}
        self._structured: Dict[str, StructuredMemory] = {}

    def add(self, item: MemoryItem) -> None:
        self._items[item.id] = item

        session_id = item.id.rsplit("_", 1)[0]
        if session_id not in self._sessions:
            self._sessions[session_id] = Session(id=session_id)
        self._sessions[session_id].messages.append(item)

    def get(self, item_id: str) -> Optional[MemoryItem]:
        return self._items.get(item_id)

    def list(self, session_id: str, limit: int = 100) -> List[MemoryItem]:
        session = self._sessions.get(session_id)
        if not session:
            return []
        return session.messages[-limit:]

    def delete(self, item_id: str) -> bool:
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False

    def update(self, item: MemoryItem) -> None:
        self._items[item.id] = item

    def get_session(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)

    def save_session(self, session: Session) -> None:
        self._sessions[session.id] = session

    def list_sessions(self, limit: int = 100) -> List[Session]:
        sessions = sorted(
            self._sessions.values(), key=lambda s: s.updated_at, reverse=True
        )
        return sessions[:limit]

    def get_structured(self, session_id: str) -> Optional[StructuredMemory]:
        return self._structured.get(session_id)

    def save_structured(self, session_id: str, structured: StructuredMemory) -> None:
        self._structured[session_id] = structured

    def clear(self) -> None:
        self._items.clear()
        self._sessions.clear()
        self._structured.clear()
