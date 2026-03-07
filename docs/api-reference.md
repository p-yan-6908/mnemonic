# API Reference

## Core Classes

### MnemonicMemory

Main entry point for memory management.

```python
MnemonicMemory(
    max_tokens: int = 128000,
    strategy: Strategy = None,
    storage: StorageBackend = None,
    encoding: str = "cl100k_base",
    session_id: str = None,
    warning_threshold: float = 0.75,
    critical_threshold: float = 0.90,
)
```

**Properties:**
- `session_id` - Current session identifier
- `token_count` - Current token count
- `message_count` - Number of messages
- `usage_ratio` - Token usage (0.0 to 1.0)

**Methods:**

#### add_message(role, content, metadata=None)

Add a message to memory.

```python
item = memory.add_message("user", "Hello", metadata={"source": "cli"})
```

#### get_context_for(query, max_tokens=None)

Get relevant context for a query.

```python
context = memory.get_context_for("what auth are we using?", max_tokens=4000)
```

#### get_recent_messages(count=10)

Get most recent messages.

```python
messages = memory.get_recent_messages(count=5)
```

#### compact()

Compact memory using strategy.

```python
result = memory.compact()
# CompactionResult(original_count, compacted_count, tokens_saved, strategy_used)
```

### TokenTracker

```python
tracker = TokenTracker(
    encoding="cl100k_base",
    max_tokens=128000,
    warning_threshold=0.75,
    critical_threshold=0.90,
)
```

**Properties:**
- `count` - Current token count
- `max_tokens` - Maximum tokens
- `usage_ratio` - Current usage (0.0 to 1.0)

**Methods:**
- `add_tokens(text)` - Add text and return token count
- `add_message(role, content)` - Add formatted message
- `remove_tokens(count)` - Remove tokens
- `reset()` - Reset counter

### Storage Classes

```python
# In-memory
storage = InMemoryStorage()

# SQLite (persistent)
storage = SQLiteEpisodicStorage("mnemonic.db")

# Vector (semantic search)
storage = InMemoryVectorStore()
```

### Strategy Classes

```python
# Built-in strategies
from mnemonic.strategies import (
    RecencyStrategy,
    ImportanceStrategy,
    SemanticRetrievalStrategy,
    HybridStrategy,
)
```

## Models

```python
from mnemonic import Message, Session, MemoryItem, Entity, Decision, OpenThread
```

See [Models](models.md) for complete schema.
