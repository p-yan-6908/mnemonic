# Mnemonic Quick Start

## Installation

```bash
pip install mnemonic
```

Or with all dependencies:

```bash
pip install mnemonic[all]
```

## Basic Usage

### Initialize Memory

```python
from mnemonic import MnemonicMemory

memory = MnemonicMemory(max_tokens=128000)
```

### Add Messages

```python
memory.add_message("user", "We're using OAuth2 for authentication")
memory.add_message("assistant", "Great choice! OAuth2 is a solid protocol")
```

### Query Context

```python
context = memory.get_context_for("what authentication are we using?")
print(context)
```

### Compaction

When token limit is reached, compact memory:

```python
result = memory.compact()
print(f"Compacted from {result.original_count} to {result.compacted_count} messages")
```

## Configuration

```python
from mnemonic import MnemonicMemory
from mnemonic.strategies import HybridStrategy

# Custom strategy
strategy = HybridStrategy(weights={
    "recency": 0.4,
    "importance": 0.4,
    "semantic": 0.2,
})

memory = MnemonicMemory(
    max_tokens=128000,
    strategy=strategy,
    warning_threshold=0.75,
    critical_threshold=0.90,
)
```

## Callbacks

```python
memory.on_warning(lambda: print("75% token limit reached"))
memory.on_critical(lambda: print("90% token limit - compact now!"))
```

## Next Steps

- [Strategies](strategies.md) - Learn about prioritization strategies
- [Storage](storage.md) - Configure persistent storage
- [Integrations](integrations.md) - Claude Code, OpenCode, MCP
