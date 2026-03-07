from typing import List, Optional, Dict, Any
import sqlite3
import json
from datetime import datetime
from pathlib import Path

from mnemonic.core.models import MemoryItem, Session, StructuredMemory, Message
from mnemonic.core.exceptions import StorageError


class SQLiteEpisodicStorage:
    def __init__(self, db_path: str = ":memory:"):
        self._db_path = db_path
        self._conn = None
        self._init_db()

    def _init_db(self):
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row

        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT DEFAULT '{}'
            )
        """)

        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT DEFAULT '{}',
                token_count INTEGER,
                importance_score REAL DEFAULT 0.5,
                entities TEXT DEFAULT '[]',
                decisions TEXT DEFAULT '[]',
                is_compacted INTEGER DEFAULT 0,
                compacted_to TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)

        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS structured_memory (
                session_id TEXT PRIMARY KEY,
                entities TEXT DEFAULT '{}',
                decisions TEXT DEFAULT '[]',
                open_threads TEXT DEFAULT '[]',
                importance_scores TEXT DEFAULT '{}',
                key_facts TEXT DEFAULT '[]',
                last_extracted TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_session 
            ON messages(session_id, timestamp)
        """)

        self._conn.commit()

    def add(self, item: MemoryItem) -> None:
        session_id = item.id.rsplit("_", 1)[0]

        self._conn.execute(
            """
            INSERT OR REPLACE INTO messages 
            (id, session_id, role, content, timestamp, metadata, token_count, 
             importance_score, entities, decisions, is_compacted, compacted_to)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                item.id,
                session_id,
                item.message.role,
                item.message.content,
                item.message.timestamp.isoformat(),
                json.dumps(item.message.metadata),
                item.message.token_count,
                item.importance_score,
                json.dumps(item.entities),
                json.dumps(item.decisions),
                1 if item.is_compacted else 0,
                item.compacted_to,
            ),
        )

        self._ensure_session(session_id)
        self._conn.commit()

    def _ensure_session(self, session_id: str):
        cursor = self._conn.execute(
            "SELECT id FROM sessions WHERE id = ?", (session_id,)
        )
        if cursor.fetchone() is None:
            now = datetime.utcnow().isoformat()
            self._conn.execute(
                "INSERT INTO sessions (id, created_at, updated_at) VALUES (?, ?, ?)",
                (session_id, now, now),
            )
            self._conn.commit()

    def get(self, item_id: str) -> Optional[MemoryItem]:
        cursor = self._conn.execute("SELECT * FROM messages WHERE id = ?", (item_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_memory_item(row)

    def _row_to_memory_item(self, row) -> MemoryItem:
        return MemoryItem(
            id=row["id"],
            message=Message(
                role=row["role"],
                content=row["content"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                token_count=row["token_count"],
            ),
            importance_score=row["importance_score"],
            entities=json.loads(row["entities"]) if row["entities"] else [],
            decisions=json.loads(row["decisions"]) if row["decisions"] else [],
            is_compacted=bool(row["is_compacted"]),
            compacted_to=row["compacted_to"],
        )

    def list(self, session_id: str, limit: int = 100) -> List[MemoryItem]:
        cursor = self._conn.execute(
            """
            SELECT * FROM messages 
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (session_id, limit),
        )

        return [self._row_to_memory_item(row) for row in cursor.fetchall()]

    def delete(self, item_id: str) -> bool:
        cursor = self._conn.execute("DELETE FROM messages WHERE id = ?", (item_id,))
        self._conn.commit()
        return cursor.rowcount > 0

    def update(self, item: MemoryItem) -> None:
        self.add(item)

    def get_session(self, session_id: str) -> Optional[Session]:
        cursor = self._conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        )
        row = cursor.fetchone()

        if row is None:
            return None

        messages = self.list(session_id, limit=10000)

        return Session(
            id=row["id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            messages=messages,
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )

    def save_session(self, session: Session) -> None:
        self._ensure_session(session.id)

        self._conn.execute(
            """
            UPDATE sessions 
            SET updated_at = ?, metadata = ?
            WHERE id = ?
        """,
            (
                session.updated_at.isoformat(),
                json.dumps(session.metadata),
                session.id,
            ),
        )

        for item in session.messages:
            self.add(item)

        self._conn.commit()

    def list_sessions(self, limit: int = 100) -> List[Session]:
        cursor = self._conn.execute(
            """
            SELECT * FROM sessions 
            ORDER BY updated_at DESC
            LIMIT ?
        """,
            (limit,),
        )

        sessions = []
        for row in cursor.fetchall():
            session = self.get_session(row["id"])
            if session:
                sessions.append(session)

        return sessions

    def get_structured(self, session_id: str) -> Optional[StructuredMemory]:
        cursor = self._conn.execute(
            "SELECT * FROM structured_memory WHERE session_id = ?", (session_id,)
        )
        row = cursor.fetchone()

        if row is None:
            return None

        return StructuredMemory(
            entities={},
            decisions=json.loads(row["decisions"]) if row["decisions"] else [],
            open_threads=json.loads(row["open_threads"]) if row["open_threads"] else [],
            importance_scores=json.loads(row["importance_scores"])
            if row["importance_scores"]
            else {},
            key_facts=json.loads(row["key_facts"]) if row["key_facts"] else [],
            last_extracted=datetime.fromisoformat(row["last_extracted"]),
        )

    def save_structured(self, session_id: str, structured: StructuredMemory) -> None:
        self._ensure_session(session_id)

        self._conn.execute(
            """
            INSERT OR REPLACE INTO structured_memory 
            (session_id, entities, decisions, open_threads, importance_scores, key_facts, last_extracted)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                session_id,
                "{}",
                json.dumps([d.dict() for d in structured.decisions]),
                json.dumps([t.dict() for t in structured.open_threads]),
                json.dumps(structured.importance_scores),
                json.dumps(structured.key_facts),
                structured.last_extracted.isoformat(),
            ),
        )
        self._conn.commit()

    def close(self):
        if self._conn:
            self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
