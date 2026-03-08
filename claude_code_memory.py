import os
import sys

from mnemonic import MnemonicMemory
from mnemonic.integrations import ClaudeCompactAdapter, MCPServer

_memory = None
_adapter = None
_mcp_server = None


def init_memory(
    max_tokens: int = 128000,
    session_id: str = None,
    auto_compact: bool = True,
    auto_compact_threshold: float = 0.75,
) -> MnemonicMemory:
    global _memory, _adapter

    _memory = MnemonicMemory(
        max_tokens=max_tokens,
        session_id=session_id,
        auto_compact=auto_compact,
        auto_compact_threshold=auto_compact_threshold,
    )

    _adapter = ClaudeCompactAdapter(_memory)

    return _memory


def get_memory() -> MnemonicMemory:
    global _memory
    if _memory is None:
        init_memory()
    return _memory


def get_adapter() -> ClaudeCompactAdapter:
    global _adapter
    if _adapter is None:
        get_memory()
    return _adapter


def add_message(role: str, content: str, metadata: dict = None):
    return get_memory().add_message(role, content, metadata)


def get_context(query: str, max_tokens: int = 4000) -> str:
    return get_memory().get_context_for(query, max_tokens)


def get_session_info() -> dict:
    memory = get_memory()
    return {
        "session_id": memory.session_id,
        "message_count": memory.message_count,
        "token_count": memory.token_count,
        "usage_ratio": memory.usage_ratio,
    }


def compact():
    return get_memory().compact()


def get_mcp_server() -> MCPServer:
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServer(get_memory())
    return _mcp_server
