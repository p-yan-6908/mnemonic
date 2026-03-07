from typing import List, Optional
from mnemonic.core.models import Message, MemoryItem


class ContextBuilder:
    def __init__(self, max_tokens: int = 128000):
        self._max_tokens = max_tokens

    def build(
        self,
        messages: List[MemoryItem],
        max_tokens: Optional[int] = None,
    ) -> str:
        if not messages:
            return ""

        limit = max_tokens or self._max_tokens
        sorted_msgs = sorted(messages, key=lambda m: m.message.timestamp)

        context_parts = []
        current_tokens = 0

        for item in sorted_msgs:
            msg = item.message
            content = f"{msg.role}: {msg.content}"
            tokens = msg.token_count or len(content.split())

            if current_tokens + tokens <= limit:
                context_parts.append(content)
                current_tokens += tokens
            else:
                break

        return "\n\n".join(context_parts)

    def build_for_query(
        self,
        messages: List[MemoryItem],
        query: str,
        max_tokens: int = 4000,
    ) -> str:
        sorted_msgs = sorted(messages, key=lambda m: m.message.timestamp)

        context_parts = []
        current_tokens = 0

        for item in sorted_msgs[-50:]:
            msg = item.message
            content = f"{msg.role}: {msg.content}"
            tokens = msg.token_count or len(content.split())

            if current_tokens + tokens <= max_tokens:
                context_parts.append(content)
                current_tokens += tokens

        return "\n\n".join(context_parts)
