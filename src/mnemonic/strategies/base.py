from typing import Protocol, List
from mnemonic.core.models import MemoryItem, Message


class Strategy(Protocol):
    def score(self, message: MemoryItem, context: List[MemoryItem]) -> float:
        raise NotImplementedError

    def select(
        self,
        messages: List[MemoryItem],
        target_tokens: int,
        token_counter,
    ) -> List[MemoryItem]:
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError
