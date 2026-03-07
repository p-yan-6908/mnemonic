"""
Mnemonic - Intelligent Memory Management for LLM Applications
"""

__version__ = "0.1.0"

from mnemonic.core.memory import MnemonicMemory
from mnemonic.core.models import (
    Message,
    Session,
    MemoryItem,
    Entity,
    Decision,
    OpenThread,
    StructuredMemory,
)
from mnemonic.core.config import MnemonicConfig
from mnemonic.core.token_tracker import TokenTracker
from mnemonic.strategies.base import Strategy
from mnemonic.strategies.recency import RecencyStrategy
from mnemonic.strategies.importance import ImportanceStrategy
from mnemonic.strategies.semantic import SemanticRetrievalStrategy
from mnemonic.strategies.hybrid import HybridStrategy
from mnemonic.storage.base import StorageBackend
from mnemonic.storage.memory import InMemoryStorage
from mnemonic.storage.episodic import SQLiteEpisodicStorage
from mnemonic.storage.vector import InMemoryVectorStore
from mnemonic.integrations.claude_code import ClaudeCompactAdapter
from mnemonic.integrations.opencoder import OpenCodeSession, OpenCodeIntegration
from mnemonic.integrations.mcp import MCPServer

__all__ = [
    "MnemonicMemory",
    "MnemonicConfig",
    "TokenTracker",
    "Message",
    "Session",
    "MemoryItem",
    "Entity",
    "Decision",
    "OpenThread",
    "StructuredMemory",
    "Strategy",
    "RecencyStrategy",
    "ImportanceStrategy",
    "SemanticRetrievalStrategy",
    "HybridStrategy",
    "StorageBackend",
    "InMemoryStorage",
    "SQLiteEpisodicStorage",
    "InMemoryVectorStore",
    "ClaudeCompactAdapter",
    "OpenCodeSession",
    "OpenCodeIntegration",
    "MCPServer",
]
