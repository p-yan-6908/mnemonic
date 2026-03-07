# Storage

Mnemonic supports multiple storage backends for different use cases.

## In-Memory Storage

Default storage - fast but non-persistent.

```python
from mnemonic import MnemonicMemory, InMemoryStorage

storage = InMemoryStorage()
memory = MnemonicMemory(storage=storage)
```

## SQLite Storage

Persistent storage for sessions.

```python
from mnemonic import MnemonicMemory
from mnemonic.storage import SQLiteEpisodicStorage

storage = SQLiteEpisodicStorage("mnemonic.db")
memory = MnemonicMemory(storage=storage)
```

## Vector Storage

Semantic search with embeddings.

```python
from mnemonic.storage import InMemoryVectorStore, SemanticSearchMixin

class SemanticMemory(SemanticSearchMixin, InMemoryVectorStore):
    pass

storage = SemanticMemory()
storage.index_messages(messages)

results = storage.semantic_search("authentication", top_k=5)
```

## Multi-Tier Architecture

```
┌─────────────────────────────────────┐
│           Working Memory             │
│         (In-Memory)                  │
│    - Lowest latency                 │
│    - Current session                │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│          Episodic Memory             │
│          (SQLite)                    │
│    - Past sessions                  │
│    - Searchable                     │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│         Semantic Memory              │
│         (Vector Store)               │
│    - Learned facts                  │
│    - Cross-session                  │
└─────────────────────────────────────┘
```

## Session Management

```python
from mnemonic.core.sessions import SessionManager

manager = SessionManager(storage)
session = manager.create_session("user-123", metadata={"user_id": "123"})
```

## Multi-Agent Shared Memory

```python
from mnemonic.core.sessions import MultiAgentCoordinator

coordinator = MultiAgentCoordinator(storage)
space = coordinator.create_shared_space("project-alpha", agent_ids=["agent1", "agent2"])

space.store_shared_entity("oauth2", "protocol", {"status": "active"})
```
