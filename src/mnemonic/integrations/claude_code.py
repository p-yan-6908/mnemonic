from typing import List, Optional, Dict, Any
from datetime import datetime

from mnemonic.core.models import MemoryItem


class ClaudeCompactAdapter:
    def __init__(self, memory):
        self._memory = memory

    def get_compact_candidates(
        self,
        max_items: int = 20,
    ) -> List[MemoryItem]:
        messages = self._memory._session.messages

        candidates = []
        for item in messages[:-5]:
            if not item.is_compacted:
                candidates.append(item)

        return candidates[:max_items]

    def compact(
        self,
        item_ids: List[str],
        summary: str,
    ) -> Dict[str, Any]:
        session = self._memory._session

        for item in session.messages:
            if item.id in item_ids:
                item.is_compacted = True

        summary_item = MemoryItem(
            id=f"{session.id}_summary_{len(session.messages)}",
            message=self._memory._session.messages[0].message.__class__(
                role="system",
                content=f"[Compacted {len(item_ids)} messages] {summary}",
            ),
            importance_score=0.8,
            is_compacted=False,
            compacted_to=None,
        )

        session.messages.append(summary_item)
        self._memory._storage.add(summary_item)

        return {
            "compacted_count": len(item_ids),
            "summary_id": summary_item.id,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_context_for_rehydration(
        self,
        max_tokens: int = 4000,
    ) -> str:
        messages = self._memory._session.messages

        summary_items = [m for m in messages if m.is_compacted]
        recent_items = messages[-5:]

        return self._memory.get_context_for(
            query="rehydration",
            max_tokens=max_tokens,
        )

    def get_working_state(self) -> Dict[str, Any]:
        messages = self._memory._session.messages

        files_being_edited = []
        todo_items = []

        for item in messages[-10:]:
            content = item.message.content.lower()

            if "editing:" in content or "edit:" in content:
                files_being_edited.append(item.message.content)

            if "todo" in content or "to-do" in content:
                todo_items.append(item.message.content)

        return {
            "recent_files": files_being_edited[-5:],
            "todo_items": todo_items[-10:],
            "message_count": len(messages),
            "session_id": self._memory.session_id,
        }
