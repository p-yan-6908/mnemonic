from typing import Optional
from dataclasses import dataclass, field


@dataclass
class MnemonicConfig:
    max_tokens: int = 128000
    encoding: str = "cl100k_base"
    warning_threshold: float = 0.75
    critical_threshold: float = 0.90
    overflow_threshold: float = 1.0
    default_strategy: str = "recency"
    storage_backend: str = "memory"
    vector_store_type: Optional[str] = None
    vector_store_path: Optional[str] = None
    session_id: Optional[str] = None
    enable_versioning: bool = False
    enable_audit: bool = False
    extraction_enabled: bool = False
    extraction_interval: int = 10
