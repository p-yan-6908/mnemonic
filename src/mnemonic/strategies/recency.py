from typing import List
from mnemonic.core.models import MemoryItem
from mnemonic.strategies.base import Strategy


class RecencyStrategy:
    @property
    def name(self) -> str:
        return "recency"

    def score(self, message: MemoryItem, context: List[MemoryItem]) -> float:
        if not context:
            return 1.0
        context_sorted = sorted(
            context, key=lambda m: m.message.timestamp, reverse=True
        )
        position = context_sorted.index(message)
        max_position = len(context_sorted) - 1
        if max_position == 0:
            return 1.0
        return 1.0 - (position / max_position)

    def select(
        self,
        messages: List[MemoryItem],
        target_tokens: int,
        token_counter,
    ) -> List[MemoryItem]:
        if not messages:
            return []

        sorted_msgs = sorted(messages, key=lambda m: m.message.timestamp, reverse=True)

        selected = []
        current_tokens = 0

        for msg in sorted_msgs:
            msg_tokens = msg.message.token_count or token_counter.count_tokens(
                msg.message.content
            )

            if current_tokens + msg_tokens <= target_tokens:
                selected.append(msg)
                current_tokens += msg_tokens
            else:
                break

        return list(reversed(selected))
