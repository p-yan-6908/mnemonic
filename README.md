# Mnemonic

Intelligent Memory Management for LLM Applications

## Overview

Mnemonic is an intelligent, adaptive context management library that actively decides WHAT to retain when LLM context windows fill up—moving beyond simple compression to a full memory architecture with prioritization, structured storage, retrieval, and multi-session persistence.

## Features

- **Token-Aware Tracking**: Real-time monitoring of token usage with configurable thresholds
- **Intelligent Strategies**: Multiple prioritization strategies (recency, importance, semantic, hybrid)
- **Structured Extraction**: Extract entities, decisions, and open threads instead of flat summaries
- **Multi-Tier Storage**: Working, episodic, and semantic memory tiers
- **Claude Code & OpenCode Compatible**: Built-in adapters for AI coding assistants
- **MCP Server**: Full Model Context Protocol integration

## Quick Start

```python
from mnemonic import MnemonicMemory

# Initialize memory with 128K context window
memory = MnemonicMemory(max_tokens=128000)

# Add messages to memory
memory.add_message("user", "We're using OAuth2 for authentication")
memory.add_message("assistant", "Great choice! OAuth2 is a solid protocol")

# Get context relevant to a query
context = memory.get_context_for("what authentication are we using?")
print(context)
```

## Installation

```bash
pip install mnemonic
```

## With Optional Dependencies

```bash
# With vector store support
pip install mnemonic[vector]

# With LLM extraction support
pip install mnemonic[llm]

# All dependencies
pip install mnemonic[all]
```

## Documentation

- [Quick Start](docs/quickstart.md)
- [Strategies](docs/strategies.md)
- [Storage](docs/storage.md)
- [API Reference](docs/api-reference.md)
- [Integrations](docs/integrations.md)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Application Layer                   │
│         (Claude Code, OpenCode, LangChain)          │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              Intelligent Memory Core                 │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │   Token     │  │  Strategy   │  │  Retrieval │ │
│  │  Tracker    │  │   Engine    │  │   Engine   │ │
│  └─────────────┘  └─────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                   Storage Layer                      │
│  ┌─────────┐  ┌──────────┐  ┌───────────────────┐│
│  │ Working │  │ Episodic │  │ Semantic / Vector ││
│  │ Memory  │  │ Memory   │  │     Store         ││
│  └─────────┘  └──────────┘  └───────────────────┘│
└─────────────────────────────────────────────────────┘
```

## License

MIT License - see LICENSE file for details
