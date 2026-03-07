# Integrations

## Claude Code

Use Claude Code's compact protocol.

```python
from mnemonic import MnemonicMemory
from mnemonic.integrations import ClaudeCompactAdapter

memory = MnemonicMemory(max_tokens=128000)
adapter = ClaudeCompactAdapter(memory)

# Get candidates for compaction
candidates = adapter.get_compact_candidates()

# Compact selected items
result = adapter.compact(
    item_ids=["msg_1", "msg_2"],
    summary="Previous OAuth2 discussion"
)

# Get context for rehydration
context = adapter.get_context_for_rehydration(max_tokens=4000)

# Get working state
state = adapter.get_working_state()
```

## OpenCode

Track OpenCode session context.

```python
from mnemonic.integrations import OpenCodeSession

session = OpenCodeSession(session_id="my-session")

# Track file context
session.track_file_context("/src/auth.py", file_content, action="editing")

# Track tool usage
session.track_tool_usage("read_file", {"path": "/src/main.py"})

# Get session summary
info = session.get_session_summary()
```

## MCP Server

Full Model Context Protocol integration.

```python
from mnemonic import MnemonicMemory
from mnemonic.integrations import MCPServer

memory = MnemonicMemory()
mcp = MCPServer(memory)

# List available tools
print(mcp.list_tools())

# Handle requests
result = mcp.handle_request("get_context", {"query": "authentication"})
result = mcp.handle_request("add_message", {"role": "user", "content": "Hello"})
result = mcp.handle_request("compact", {})
result = mcp.handle_request("get_session_info", {})

# Get tool schemas
schema = mcp.get_tool_schema("get_context")
```

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `get_context` | Get relevant memory for query |
| `add_message` | Add message to memory |
| `get_recent_messages` | Get recent messages |
| `compact` | Compact memory |
| `get_session_info` | Session statistics |
| `search_memory` | Search memory |

## LangChain Integration

```python
# Mnemonic is compatible with LangChain memory interfaces
# Use as drop-in replacement for ConversationBufferMemory
```
