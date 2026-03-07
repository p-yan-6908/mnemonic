from typing import Protocol, List, Optional
from datetime import datetime
from mnemonic.core.models import MemoryItem, Session, StructuredMemory


class StorageBackend(Protocol):
    def add(self, item: MemoryItem) -> None:
        raise NotImplementedError

    def get(self, item_id: str) -> Optional[MemoryItem]:
        raise NotImplementedError

    def list(self, session_id: str, limit: int = 100) -> List[MemoryItem]:
        raise NotImplementedError

    def delete(self, item_id: str) -> bool:
        raise NotImplementedError

    def update(self, item: MemoryItem) -> None:
        raise NotImplementedError

    def get_session(self, session_id: str) -> Optional[Session]:
        raise NotImplementedError

    def save_session(self, session: Session) -> None:
        raise NotImplementedError

    def list_sessions(self, limit: int = 100) -> List[Session]:
        raise NotImplementedError

    def get_structured(self, session_id: str) -> Optional[StructuredMemory]:
        raise NotImplementedError

    def save_structured(self, session_id: str, structured: StructuredMemory) -> None:
        raise NotImplementedError
