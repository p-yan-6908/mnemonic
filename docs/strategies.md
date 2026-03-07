# Strategies

Mnemonic provides multiple strategies for deciding what to keep when memory needs to be compacted.

## Available Strategies

### RecencyStrategy

Keep the most recent messages. Simple and predictable.

```python
from mnemonic.strategies import RecencyStrategy

strategy = RecencyStrategy()
```

**Best for:** Chat applications where recent context matters most.

### ImportanceStrategy

Score messages based on keywords, role, and content length.

```python
from mnemonic.strategies import ImportanceStrategy

strategy = ImportanceStrategy(
    importance_keywords=["important", "critical", "remember", "decided"]
)
```

**Features:**
- Keyword boosting
- Assistant messages score higher
- Longer content prioritized

### SemanticRetrievalStrategy

Use semantic similarity to keep messages relevant to likely future queries.

```python
from mnemonic.strategies import SemanticRetrievalStrategy

strategy = SemanticRetrievalStrategy(top_k=10)
```

**Best for:** Knowledge retrieval, Q&A systems.

### HybridStrategy

Combine multiple strategies with configurable weights.

```python
from mnemonic.strategies import HybridStrategy

strategy = HybridStrategy(weights={
    "recency": 0.4,
    "importance": 0.3,
    "semantic": 0.3,
})
```

## Custom Strategy

Implement your own strategy:

```python
from mnemonic.strategies.base import Strategy

class MyStrategy:
    @property
    def name(self) -> str:
        return "my_strategy"
    
    def score(self, message, context):
        # Return 0.0 to 1.0
        return 0.5
    
    def select(self, messages, target_tokens, token_counter):
        # Return filtered messages
        return messages
```

## Usage

```python
from mnemonic import MnemonicMemory
from mnemonic.strategies import HybridStrategy

memory = MnemonicMemory(
    max_tokens=128000,
    strategy=HybridStrategy()
)
```
