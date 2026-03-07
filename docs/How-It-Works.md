# How Mnemonic Works

Understanding the architecture and internal mechanics of Mnemonic.

## Core Concepts

### The Memory Problem

When building LLM applications, context windows have limits:
- GPT-4: 128K tokens
- Claude: 200K tokens
- Gemini: 1M tokens

But conversations grow unbounded. Traditional solutions:
- **Truncation**: Lose all history
- **Summarization**: Lose specificity
- **Fixed Window**: Lose early context

Mnemonic solves this with **intelligent memory management**.

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  Application Layer                    │
│    (Claude Code, OpenCode, Your App)                │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              MnemonicMemory Core                      │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │   Token     │  │  Strategy   │  │  Retrieval │ │
│  │  Tracker    │  │   Engine    │  │   Engine   │ │
│  └─────────────┘  └─────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                   Storage Layer                       │
│  ┌─────────┐  ┌──────────┐  ┌───────────────────┐ │
│  │ Working  │  │ Episodic │  │ Semantic/Vector   │ │
│  │ Memory   │  │ Memory   │  │     Store        │ │
│  └─────────┘  └──────────┘  └───────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## Step-by-Step Flow

### 1. Adding Messages

```python
memory.add_message("user", "We're using OAuth2 for authentication")
```

What happens internally:

1. **Token Counting**: TikToken encodes the message
   ```
   "user: We're using OAuth2 for authentication"
   → [2103, 467, 5278, 28430, 2, 19985, 74, 11640, 30]
   → 9 tokens
   ```

2. **Token Tracking**: Counter increments
   ```
   Before: 0 tokens
   After:  9 tokens (0.007% of 128K)
   ```

3. **Storage**: Message saved to Working Memory
   ```
   MemoryItem(
     id="session_001_0",
     role="user",
     content="We're using OAuth2 for authentication",
     importance_score=0.15,  # Initial default
     timestamp=2024-01-15T10:30:00Z
   )
   ```

### 2. Querying Context

```python
context = memory.get_context_for("what auth are we using?")
```

Internal flow:

1. **Retrieve Messages**: Fetch from Working Memory
2. **Sort by Relevance**: Strategy scores each message
3. **Build Context**: Concatenate until token limit
4. **Return**: Formatted context string

### 3. Compaction (When Memory Fills)

Triggered when `usage_ratio >= warning_threshold` (default 75%):

```python
result = memory.compact()
```

#### Strategy Execution

**RecencyStrategy:**
```
1. Sort messages by timestamp (newest first)
2. Add to result until target tokens reached
3. Return selected messages
```

**ImportanceStrategy:**
```
1. Score each message:
   - Keyword matches: +0.15 per keyword
   - Assistant role: +0.1
   - System role: +0.2
   - Content length: +0.2 max
2. Sort by score (highest first)
3. Add to result until target tokens reached
```

**HybridStrategy:**
```
1. For each message:
   - recency_score × 0.4
   - importance_score × 0.3
   - semantic_score × 0.3
   = final_score
2. Sort by final_score
3. Add to result until target tokens reached
```

## Data Models

### Message Flow

```
User Input
    │
    ▼
Message (role, content, metadata)
    │
    ▼
MemoryItem (+id, +importance_score, +timestamp)
    │
    ▼
Storage (InMemory / SQLite / Vector)
```

### Structured Memory Extraction

Mnemonic extracts structured knowledge from conversations:

```python
structured = {
    "entities": {
        "oauth2": {
            "type": "protocol",
            "status": "active",
            "importance_score": 0.9
        }
    },
    "decisions": [
        {
            "statement": "Use Auth0 for OAuth",
            "rationale": "Better enterprise support",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    ],
    "open_threads": [
        {
            "topic": "refresh_tokens",
            "question": "How to implement rotation?"
        }
    ]
}
```

Extracted via:
- **EntityExtractor**: Regex + keyword matching
- **DecisionTracker**: Pattern matching for decision phrases
- **OpenThreadDetector**: Question detection

## Storage Tiers

### Tier 1: Working Memory
- **Location**: In-Memory (RAM)
- **Latency**: <1ms
- **Capacity**: Configurable (default 50% of context)
- **Use**: Current conversation

### Tier 2: Episodic Memory
- **Location**: SQLite (disk)
- **Latency**: ~10ms
- **Capacity**: Unlimited
- **Use**: Past sessions, searchable

### Tier 3: Semantic Memory
- **Location**: Vector Store (ChromaDB/Weaviate)
- **Latency**: ~50ms
- **Capacity**: Unlimited
- **Use**: Cross-session facts, embeddings

## Integration Points

### Claude Code Compact Protocol

Claude Code calls these methods:

```python
adapter = ClaudeCompactAdapter(memory)

# 1. Get candidates for compaction
candidates = adapter.get_compact_candidates(max_items=20)

# 2. Compact selected (Claude generates summary)
adapter.compact(item_ids=[...], summary="...")

# 3. Rehydrate on resume
context = adapter.get_context_for_rehydration()
```

### MCP Server

Standard JSON-RPC interface:

```json
{
  "tool": "get_context",
  "params": {
    "query": "authentication",
    "max_tokens": 4000
  }
}
```

## Configuration

### Token Thresholds

```
0% ───────────────────────────────────── 100%
    │           │         │
    │ warning   │critical│ overflow
   75%        90%       100%
```

Callbacks fire at each threshold:
```python
memory.on_warning(lambda: print("75% - start preparing"))
memory.on_critical(lambda: print("90% - compact now!"))
memory.on_overflow(lambda: print("100% - emergency"))
```

### Strategy Selection

| Use Case | Recommended Strategy |
|----------|-------------------|
| Simple chat | RecencyStrategy |
| Technical discussions | ImportanceStrategy |
| Knowledge base | SemanticRetrievalStrategy |
| Production apps | HybridStrategy |

## Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| add_message | <1ms | In-memory |
| get_context_for | <10ms | Depends on message count |
| compact | <100ms | 1K messages |
| SQLite query | ~10ms | Disk I/O |
| Vector search | ~50ms | Embedding computation |

## Extending Mnemonic

### Custom Strategy

```python
from mnemonic.strategies.base import Strategy

class MyStrategy:
    @property
    def name(self): return "my_custom"
    
    def score(self, message, context):
        # Your logic
        return 0.5
    
    def select(self, messages, target_tokens, token_counter):
        # Your selection logic
        return messages[:10]
```

### Custom Storage

```python
from mnemonic.storage.base import StorageBackend

class MyStorage(StorageBackend):
    def add(self, item): ...
    def get(self, item_id): ...
    def list(self, session_id, limit): ...
    # Implement all protocol methods
```
