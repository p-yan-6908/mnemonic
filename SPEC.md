# Mnemonic - Intelligent Memory Management for LLM Applications

## Project Overview

**Project Name:** Mnemonic  
**Type:** Python Library (AI/ML Developer Tool)  
**Core Functionality:** An intelligent, adaptive context management library that actively decides WHAT to retain when LLM context windows fill up—moving beyond simple compression to a full memory architecture with prioritization, structured storage, retrieval, and multi-session persistence.  
**Target Users:** AI developers building LLM-powered applications, AI coding assistants (Claude Code, OpenCode, Cursor, etc.), autonomous agents, and chat systems.

---

## Problem Statement

### The Core Problem

Current LLM memory solutions are crude and lossy. When context windows fill up, developers face:

| Approach | Problem |
|----------|---------|
| **Truncation** | Lose all history - complete context loss |
| **Flat Summarization** | Lose specificity - important details vanish |
| **Naive Windows** | Keep recent, drop everything else - loses critical early context |
| **Fixed Buffers** | No intelligence about what matters |

### Why This Matters Now

1. **Agentic Apps Exploding**: AI agents need human-like memory capabilities
2. **1M+ Token Contexts**: Larger contexts create management complexity
3. **Cost Pressure**: Storing irrelevant context wastes tokens = money
4. **Multi-session Requirements**: Users expect persistent memory across sessions

---

## Solution: Mnemonic Architecture

### Design Philosophy

Mnemonic follows three core principles:

1. **Intelligence Over Compression**: Not "how do we fit more" but "what matters most"
2. **Structured Over Flat**: Extract knowledge, not just compress text
3. **Developer Experience First**: Simple API, powerful defaults, extensible

### Core Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Application Layer                              │
│   (Claude Code, OpenCode, LangChain, LlamaIndex, Custom AI Apps)   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Mnemonic Core API                                │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐    │
│  │   Memory       │  │   Context      │  │    Retrieval      │    │
│  │   Manager      │  │   Builder      │  │    Engine         │    │
│  └────────────────┘  └────────────────┘  └────────────────────┘    │
│            │                  │                     │               │
│            ▼                  ▼                     ▼               │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Strategy Engine                           │   │
│  │  [Recency] [Importance] [Semantic] [Hybrid] [Custom]       │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Storage Layer                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────────────────┐  │
│  │   Working   │  │  Episodic   │  │      Semantic / Vector    │  │
│  │   Memory    │  │   Memory    │  │  (Chroma, Weaviate,      │  │
│  │  (In-Mem)  │  │  (Session)  │  │   Pinecone, Qdrant)       │  │
│  └─────────────┘  └─────────────┘  └────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Feature Specifications

### 1. Token-Aware Memory Tracking

**Description:** Real-time monitoring of token usage with configurable management triggers.

**Specifications:**
- `TokenTracker` class monitors current token count
- Supported encodings: cl100k_base, p50k_base, r50k_base
- Configurable thresholds: warning (75%), critical (90%), overflow (100%)
- Support for context windows: 4K, 8K, 32K, 64K, 128K, 200K, 1M tokens
- Event hooks: `on_warning`, `on_critical`, `on_overflow`

**API:**
```python
tracker = TokenTracker(encoding="cl100k_base", max_tokens=128000)
tracker.add_message("user", "Hello world")
current_tokens = tracker.count
tracker.on_warning(lambda: print("75% threshold reached"))
```

### 2. Intelligent Prioritization Strategies

**Description:** Multiple strategies for deciding what to keep when memory pressure occurs.

#### Strategy 1: RecencyStrategy
- Keep most recent messages
- Simple, predictable, low-latency
- Best for: Chat applications, temporal contexts

#### Strategy 2: ImportanceStrategy
- AI-powered relevance scoring
- Uses embeddings to score semantic importance
- Configurable importance model (OpenAI, Anthropic, local)
- Best for: Technical discussions, decision-making

#### Strategy 3: SemanticRetrievalStrategy
- Predict future queries based on current context
- Use embedding similarity to keep relevant content
- Best for: Knowledge retrieval, Q&A systems

#### Strategy 4: HybridStrategy
- Combine multiple signals with configurable weights
- Example: 40% recency + 30% importance + 30% semantic
- Best for: Production systems requiring balance

#### Strategy 5: CustomStrategy
- Plugin interface for custom prioritization logic
- `Strategy` protocol with `score()` method

### 3. Structured Memory Extraction

**Description:** Extract structured knowledge instead of flat summaries.

**Extraction Schema:**
```python
class StructuredMemory(BaseModel):
    entities: Dict[str, Entity] = {}
    decisions: List[Decision] = []
    open_threads: List[OpenThread] = []
    importance_scores: Dict[str, float] = {}
    key_facts: List[KeyFact] = []

class Entity(BaseModel):
    name: str
    type: str  # protocol, tool, library, person, concept
    status: Optional[str] = None
    attributes: Dict[str, Any] = {}

class Decision(BaseModel):
    statement: str
    rationale: Optional[str] = None
    timestamp: datetime
    participants: List[str] = []

class OpenThread(BaseModel):
    topic: str
    question: str
    related_entities: List[str] = []
    first_mentioned: int  # message index
```

**Example Output:**
```json
{
  "entities": {
    "oauth2": {"type": "protocol", "status": "blocked", "attributes": {"flow": "authorization_code"}},
    "auth0": {"type": "provider", "status": "selected", "attributes": {"tier": "enterprise"}}
  },
  "decisions": [
    {"statement": "Use Auth0 for OAuth provider", "rationale": "Better enterprise support", "timestamp": "2024-01-15T10:30:00Z"}
  ],
  "open_threads": [
    {"topic": "refresh_tokens", "question": "How to implement refresh token rotation?"}
  ],
  "importance_scores": {
    "oauth2_flow": 0.95,
    "ui_colors": 0.15,
    "auth_provider": 0.92
  }
}
```

### 4. Multi-Tier Storage Architecture

**Tier 1: Working Memory**
- Current conversation context
- Lowest latency access
- In-memory storage with optional LRU cache
- Size: Configurable (default: 50% of context window)

**Tier 2: Episodic Memory**
- Past sessions, archived conversations
- Retrievable on demand
- Storage: SQLite, PostgreSQL, or file-based
- Index: By timestamp, session ID, entity tags

**Tier 3: Semantic Memory**
- Learned facts, entities, decisions
- Shared across all sessions
- Vector embeddings for similarity search
- Storage: ChromaDB, Weaviate, Pinecone, Qdrant

### 5. Retrieval API

**Description:** Query memory at any time to get relevant context.

**API:**
```python
# Get context for a specific query
context = memory.get_context_for(
    query="what did we decide about auth?",
    max_tokens=4000,
    include_types=["decisions", "entities"]
)

# Get recent context
recent = memory.get_recent_messages(count=10)

# Get full session memory
session = memory.get_session(session_id="abc123")

# Search by entity
auth_related = memory.get_by_entity("oauth2")
```

---

## Claude Code / OpenCode Compatibility

### Design for AI Coding Assistants

Mnemonic is designed from the ground up to work WITH AI coding assistants:

### 1. MCP Server Integration
```python
# mnemonic/server.py
from fastmcp import FastMCP

mcp = FastMCP("mnemonic-memory")

@mcp.tool()
async def get_context(query: str, max_tokens: int = 4000) -> str:
    """Get relevant memory context for the current task"""
    memory = get_memory_instance()
    return memory.get_context_for(query, max_tokens)

@mcp.tool()
async def store_decision(decision: str, rationale: str = None) -> bool:
    """Store a decision in semantic memory"""
    memory = get_memory_instance()
    memory.store_decision(decision, rationale)
    return True
```

### 2. Claude Code Compact Integration
```python
# Support Claude Code's compact protocol
class ClaudeCompactAdapter:
    """Adapter for Claude Code's memory compact protocol"""
    
    def __init__(self, memory: MnemonicMemory):
        self.memory = memory
    
    def get_compact_candidates(self) -> List[MemoryItem]:
        """Return candidates for compaction"""
        return self.memory.get_compact_candidates()
    
    def compact(self, items: List[str]) -> CompactedMemory:
        """Perform compaction on selected items"""
        return self.memory.compact(items)
```

### 3. OpenCode Session Integration
```python
# Track OpenCode session context
class OpenCodeSession:
    """OpenCode-specific session management"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.memory = MnemonicMemory(session_id=f"opencoder_{session_id}")
    
    def track_file_context(self, file_path: str, content: str):
        """Track current file being edited"""
        self.memory.add_message("system", f"Editing: {file_path}")
    
    def track_tool_usage(self, tool: str, args: dict):
        """Track tool invocations"""
        self.memory.add_message("system", f"Tool: {tool}({args})")
```

### 4. Automatic Context Awareness
```python
# Detect and remember project patterns
class ProjectContextTracker:
    """Automatically learn project structure"""
    
    def __init__(self, memory: MnemonicMemory):
        self.memory = memory
        self.project_patterns = {}
    
    def learn_from_file(self, file_path: str, imports: List[str]):
        """Learn import patterns from codebase"""
        # Extract and store entity knowledge
        for imp in imports:
            self.memory.upsert_entity(imp, {"type": "dependency"})
    
    def get_relevant_context(self, current_file: str) -> List[str]:
        """Get context relevant to current file"""
        return self.memory.get_by_entity(current_file)
```

---

## Implementation Phases

### Phase 1: Core MVP (Weeks 1-2)

**Goal:** Minimal working implementation with basic functionality

**Deliverables:**
- [ ] TokenTracker with tiktoken integration
- [ ] RecencyStrategy implementation
- [ ] Basic MemoryStore (in-memory)
- [ ] Simple context builder
- [ ] Unit tests for core components
- [ ] Basic documentation

**Dependencies:**
- `tiktoken` - Token counting
- `pydantic` - Data models

### Phase 2: Intelligent Strategies (Weeks 3-4)

**Goal:** AI-powered prioritization

**Deliverables:**
- [ ] ImportanceStrategy with embedding-based scoring
- [ ] SemanticRetrievalStrategy with vector similarity
- [ ] HybridStrategy combining multiple signals
- [ ] Strategy configuration API
- [ ] Performance benchmarks

**Dependencies:**
- `numpy` - Vector operations
- `sentence-transformers` - Local embeddings (optional)

### Phase 3: Structured Extraction (Weeks 5-6)

**Goal:** Extract structured knowledge

**Deliverables:**
- [ ] Entity extraction from messages
- [ ] Decision tracking system
- [ ] Open thread detection
- [ ] Importance score aggregation
- [ ] Structured memory serialization

**Dependencies:**
- `openai` or `anthropic` - LLM for extraction (optional)
- `langchain` or `llama-index` - Integration (optional)

### Phase 4: Multi-Tier Storage (Weeks 7-8)

**Goal:** Persistent, retrievable memory

**Deliverables:**
- [ ] EpisodicMemory with SQLite backend
- [ ] SemanticMemory with vector store integration
- [ ] ChromaDB adapter
- [ ] Weaviate adapter
- [ ] Multi-session management
- [ ] Migration utilities

**Dependencies:**
- `chromadb` - Vector store
- `weaviate-client` - Vector store
- `sqlalchemy` - Database ORM

### Phase 5: Production Polish (Weeks 9-10)

**Goal:** Production-ready library

**Deliverables:**
- [ ] MCP server implementation
- [ ] Claude Code adapter
- [ ] Comprehensive test suite
- [ ] Performance optimization
- [ ] Error handling and edge cases
- [ ] Documentation website
- [ ] PyPI publication

**Dependencies:**
- `fastmcp` - MCP server
- `pytest` - Testing
- `pytest-benchmark` - Performance

---

## API Reference

### Core Classes

```python
# Main entry point
class MnemonicMemory:
    def __init__(
        self,
        max_tokens: int = 128000,
        strategy: Strategy = None,
        storage: StorageBackend = None,
        encoding: str = "cl100k_base"
    )
    
    def add_message(self, role: str, content: str, metadata: dict = None) -> None
    def get_context_for(self, query: str, max_tokens: int = None) -> str
    def get_recent_messages(self, count: int = 10) -> List[Message]
    def compact(self) -> CompactionResult
    def get_session(self, session_id: str) -> Session
    def store_decision(self, decision: str, rationale: str = None) -> None
    def upsert_entity(self, name: str, data: dict) -> None
```

### Storage Backends

```python
class InMemoryStorage(StorageBackend):
    """In-memory storage for testing/development"""

class SQLiteStorage(StorageBackend):
    """Persistent storage using SQLite"""

class VectorStorage(StorageBackend):
    """Vector-backed semantic storage"""
```

### Strategy Protocol

```python
class Strategy(Protocol):
    def score(self, message: Message, context: List[Message]) -> float:
        """Return importance score 0-1"""
        ...
    
    def select(
        self, 
        messages: List[Message], 
        target_tokens: int
    ) -> List[Message]:
        """Select messages to keep"""
        ...
```

---

## Success Criteria

### Functional Requirements
- [ ] Token counting accurate within 1% of tiktoken
- [ ] RecencyStrategy maintains message order
- [ ] ImportanceStrategy produces sensible rankings
- [ ] Structured extraction captures entities/decisions
- [ ] Retrieval returns relevant context within 100ms

### Performance Requirements
- [ ] < 10ms overhead per message addition
- [ ] < 100ms for context retrieval
- [ ] < 1s for compaction on 10K message history

### Compatibility Requirements
- [ ] Works with Python 3.9+
- [ ] Compatible with LangChain memory interface
- [ ] MCP server functional
- [ ] Claude Code adapter functional

---

## File Structure

```
mnemonic/
├── pyproject.toml
├── README.md
├── LICENSE
├── docs/
│   ├── index.md
│   ├── quickstart.md
│   ├── strategies.md
│   ├── storage.md
│   ├── api-reference.md
│   └── integrations.md
├── src/
│   └── mnemonic/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── memory.py
│       │   ├── token_tracker.py
│       │   └── context_builder.py
│       ├── strategies/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── recency.py
│       │   ├── importance.py
│       │   ├── semantic.py
│       │   └── hybrid.py
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── memory.py
│       │   ├── episodic.py
│       │   └── vector.py
│       ├── extraction/
│       │   ├── __init__.py
│       │   ├── entities.py
│       │   ├── decisions.py
│       │   └── threads.py
│       └── integrations/
│           ├── __init__.py
│           ├── mcp.py
│           ├── claude_code.py
│           └── langchain.py
├── tests/
│   ├── __init__.py
│   ├── test_token_tracker.py
│   ├── test_strategies.py
│   ├── test_storage.py
│   └── test_integration.py
└── examples/
    ├── basic_usage.py
    ├── with_langchain.py
    ├── with_claude_code.py
    └── structured_extraction.py
```

---

## Competitive Analysis

| Feature | LangChain Memory | Mem0 | Mnemonic |
|---------|------------------|------|----------|
| Token tracking | ❌ | Partial | ✅ Full |
| Importance scoring | ❌ | ✅ | ✅ |
| Structured extraction | ❌ | ❌ | ✅ |
| Multi-tier storage | ❌ | ✅ | ✅ |
| MCP integration | ❌ | ❌ | ✅ |
| Claude Code adapter | ❌ | ❌ | ✅ |
| Hybrid strategies | ❌ | ✅ | ✅ |
| Custom strategies | ✅ | ❌ | ✅ |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Token counting inaccuracies | Use tiktoken (OpenAI's library) |
| LLM cost for importance scoring | Offer multiple backends, local embeddings option |
| Vector store complexity | Provide in-memory fallback, simple API |
| Performance at scale | Async operations, caching, batch processing |

---

## Future Considerations (Post-MVP)

- [ ] WebSocket server for real-time memory sync
- [ ] Graph-based entity relationship tracking
- [ ] Multi-modal memory (images, files)
- [ ] Federated learning for importance scoring
- [ ] Memory versioning and diff
- [ ] Export/import formats (JSON, Markdown)
