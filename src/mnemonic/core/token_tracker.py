from typing import Callable, Optional
import tiktoken


class TokenTracker:
    def __init__(
        self,
        encoding: str = "cl100k_base",
        max_tokens: int = 128000,
        warning_threshold: float = 0.75,
        critical_threshold: float = 0.90,
    ):
        self._encoding = tiktoken.get_encoding(encoding)
        self._max_tokens = max_tokens
        self._warning_threshold = warning_threshold
        self._critical_threshold = critical_threshold
        self._current_tokens = 0
        self._on_warning: Optional[Callable[[], None]] = None
        self._on_critical: Optional[Callable[[], None]] = None
        self._on_overflow: Optional[Callable[[], None]] = None
        self._warning_fired = False
        self._critical_fired = False

    @property
    def count(self) -> int:
        return self._current_tokens

    @property
    def max_tokens(self) -> int:
        return self._max_tokens

    @property
    def usage_ratio(self) -> float:
        return self._current_tokens / self._max_tokens

    def count_tokens(self, text: str) -> int:
        return len(self._encoding.encode(text))

    def add_tokens(self, text: str) -> int:
        tokens = self.count_tokens(text)
        self._current_tokens += tokens
        self._check_thresholds()
        return tokens

    def add_message(self, role: str, content: str) -> int:
        formatted = f"{role}: {content}"
        return self.add_tokens(formatted)

    def remove_tokens(self, tokens: int) -> None:
        self._current_tokens = max(0, self._current_tokens - tokens)
        self._warning_fired = self.usage_ratio < self._warning_threshold
        self._critical_fired = self.usage_ratio < self._critical_threshold

    def remove_text(self, text: str) -> int:
        tokens = self.count_tokens(text)
        self.remove_tokens(tokens)
        return tokens

    def reset(self) -> None:
        self._current_tokens = 0
        self._warning_fired = False
        self._critical_fired = False

    def on_warning(self, callback: Callable[[], None]) -> None:
        self._on_warning = callback

    def on_critical(self, callback: Callable[[], None]) -> None:
        self._on_critical = callback

    def on_overflow(self, callback: Callable[[], None]) -> None:
        self._on_overflow = callback

    def _check_thresholds(self) -> None:
        ratio = self.usage_ratio

        if ratio >= self._max_tokens and self._on_overflow:
            self._on_overflow()
        elif ratio >= self._critical_threshold and not self._critical_fired:
            self._critical_fired = True
            if self._on_critical:
                self._on_critical()
        elif ratio >= self._warning_threshold and not self._warning_fired:
            self._warning_fired = True
            if self._on_warning:
                self._on_warning()

    def is_warning(self) -> bool:
        return self.usage_ratio >= self._warning_threshold

    def is_critical(self) -> bool:
        return self.usage_ratio >= self._critical_threshold

    def is_overflow(self) -> bool:
        return self.usage_ratio >= 1.0
