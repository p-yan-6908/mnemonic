from typing import Optional, List, Callable
from datetime import datetime
import uuid

from mnemonic.core.config import MnemonicConfig
from mnemonic.core.models import (
    Message,
    Session,
    MemoryItem,
    StructuredMemory,
    CompactionResult,
)
from mnemonic.core.token_tracker import TokenTracker
from mnemonic.core.context_builder import ContextBuilder
from mnemonic.strategies.base import Strategy
from mnemonic.strategies.recency import RecencyStrategy
from mnemonic.storage.base import StorageBackend
from mnemonic.storage.memory import InMemoryStorage
from mnemonic.core.exceptions import MemoryFullError


class MnemonicMemory:
    def __init__(
        self,
        max_tokens: int = 128000,
        strategy: Optional[Strategy] = None,
        storage: Optional[StorageBackend] = None,
        encoding: str = "cl100k_base",
        session_id: Optional[str] = None,
        warning_threshold: float = 0.75,
        critical_threshold: float = 0.90,
    ):
        self._config = MnemonicConfig(
            max_tokens=max_tokens,
            encoding=encoding,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
            session_id=session_id or str(uuid.uuid4()),
        )

        self._token_tracker = TokenTracker(
            encoding=encoding,
            max_tokens=max_tokens,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
        )

        self._strategy = strategy or RecencyStrategy()
        self._storage = storage or InMemoryStorage()
        self._context_builder = ContextBuilder(max_tokens=max_tokens)

        self._session = Session(id=self._config.session_id)
        self._storage.save_session(self._session)

    @property
    def session_id(self) -> str:
        return self._session.id

    @property
    def token_count(self) -> int:
        return self._token_tracker.count

    @property
    def message_count(self) -> int:
        return len(self._session.messages)

    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[dict] = None,
    ) -> MemoryItem:
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {},
        )

        tokens = self._token_tracker.add_message(role, content)
        message.token_count = tokens

        item = self._session.add_message(message)
        self._storage.add(item)

        return item

    def get_context_for(
        self,
        query: str,
        max_tokens: Optional[int] = None,
    ) -> str:
        return self._context_builder.build_for_query(
            self._session.messages,
            query,
            max_tokens or 4000,
        )

    def get_recent_messages(self, count: int = 10) -> List[Message]:
        return [item.message for item in self._session.messages[-count:]][::-1]

    def compact(self) -> CompactionResult:
        original_count = len(self._session.messages)

        if original_count == 0:
            return CompactionResult(
                original_count=0,
                compacted_count=0,
                tokens_saved=0,
                strategy_used=self._strategy.name,
            )

        target_tokens = int(self._config.max_tokens * 0.5)

        selected = self._strategy.select(
            self._session.messages,
            target_tokens,
            self._token_tracker,
        )

        compacted_count = len(selected)

        self._session.messages = selected
        self._storage.save_session(self._session)

        original_tokens = self._token_tracker.count
        self._token_tracker.reset()

        for item in selected:
            self._token_tracker.add_tokens(item.message.content)

        tokens_saved = original_tokens - self._token_tracker.count

        return CompactionResult(
            original_count=original_count,
            compacted_count=compacted_count,
            tokens_saved=tokens_saved,
            strategy_used=self._strategy.name,
        )

    def get_session(self, session_id: str) -> Optional[Session]:
        return self._storage.get_session(session_id)

    def get_all_sessions(self, limit: int = 100) -> List[Session]:
        return self._storage.list_sessions(limit)

    def get_structured(self) -> StructuredMemory:
        return self._storage.get_structured(self._session.id) or StructuredMemory()

    def save_structured(self, structured: StructuredMemory) -> None:
        self._storage.save_structured(self._session.id, structured)

    def on_warning(self, callback: Callable[[], None]) -> None:
        self._token_tracker.on_warning(callback)

    def on_critical(self, callback: Callable[[], None]) -> None:
        self._token_tracker.on_critical(callback)

    def on_overflow(self, callback: Callable[[], None]) -> None:
        self._token_tracker.on_overflow(callback)

    def is_warning(self) -> bool:
        return self._token_tracker.is_warning()

    def is_critical(self) -> bool:
        return self._token_tracker.is_critical()

    def is_overflow(self) -> bool:
        return self._token_tracker.is_overflow()

    @property
    def usage_ratio(self) -> float:
        return self._token_tracker.usage_ratio
