from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)
    token_count: Optional[int] = None

    def __str__(self) -> str:
        return f"{self.role}: {self.content[:50]}..."


class Entity(BaseModel):
    name: str
    entity_type: str
    status: Optional[str] = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    first_mentioned: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    importance_score: float = 0.5


class Decision(BaseModel):
    statement: str
    rationale: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    participants: list[str] = Field(default_factory=list)
    status: str = "active"


class OpenThread(BaseModel):
    topic: str
    question: str
    related_entities: list[str] = Field(default_factory=list)
    first_mentioned: datetime = Field(default_factory=datetime.utcnow)
    last_mentioned: datetime = Field(default_factory=datetime.utcnow)


class StructuredMemory(BaseModel):
    entities: dict[str, Entity] = Field(default_factory=dict)
    decisions: list[Decision] = Field(default_factory=list)
    open_threads: list[OpenThread] = Field(default_factory=list)
    importance_scores: dict[str, float] = Field(default_factory=dict)
    key_facts: list[str] = Field(default_factory=list)
    last_extracted: datetime = Field(default_factory=datetime.utcnow)


class MemoryItem(BaseModel):
    id: str
    message: Message
    importance_score: float = 0.5
    entities: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)
    is_compacted: bool = False
    compacted_to: Optional[str] = None


class Session(BaseModel):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    messages: list[MemoryItem] = Field(default_factory=list)
    structured: StructuredMemory = Field(default_factory=StructuredMemory)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def add_message(self, message: Message) -> MemoryItem:
        item = MemoryItem(
            id=f"{self.id}_{len(self.messages)}",
            message=message,
        )
        self.messages.append(item)
        self.updated_at = datetime.utcnow()
        return item


class CompactionResult(BaseModel):
    original_count: int
    compacted_count: int
    tokens_saved: int
    strategy_used: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
