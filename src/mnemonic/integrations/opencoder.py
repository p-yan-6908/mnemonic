from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from mnemonic.core.memory import MnemonicMemory


class OpenCodeSession:
    def __init__(
        self,
        session_id: Optional[str] = None,
        max_tokens: int = 128000,
        **kwargs,
    ):
        self._session_id = session_id or f"opencoder_{uuid.uuid4().hex[:8]}"
        self._memory = MnemonicMemory(
            session_id=self._session_id,
            max_tokens=max_tokens,
            **kwargs,
        )
        self._file_context: Dict[str, str] = {}
        self._tool_history: List[Dict] = []

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def memory(self) -> MnemonicMemory:
        return self._memory

    def track_file_context(
        self,
        file_path: str,
        content: str,
        action: str = "viewing",
    ) -> None:
        self._file_context[file_path] = content

        self._memory.add_message(
            role="system",
            content=f"[{action.capitalize()}] {file_path}",
            metadata={
                "type": "file_context",
                "file_path": file_path,
                "action": action,
            },
        )

    def track_tool_usage(
        self,
        tool: str,
        args: Dict[str, Any],
        result: Optional[Any] = None,
    ) -> None:
        tool_entry = {
            "tool": tool,
            "args": args,
            "timestamp": datetime.utcnow().isoformat(),
        }

        self._tool_history.append(tool_entry)

        args_str = str(args)[:200]
        self._memory.add_message(
            role="system",
            content=f"Tool: {tool}({args_str})",
            metadata={
                "type": "tool_usage",
                "tool": tool,
            },
        )

    def get_current_file(self) -> Optional[str]:
        return self._last_file_with_action("editing")

    def _last_file_with_action(self, action: str) -> Optional[str]:
        messages = self._memory._session.messages

        for msg in reversed(messages):
            metadata = msg.message.metadata
            if metadata.get("type") == "file_context":
                if metadata.get("action") == action:
                    return metadata.get("file_path")

        return None

    def get_tool_history(
        self,
        tool: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict]:
        if tool:
            return [t for t in self._tool_history[-limit:] if t["tool"] == tool]
        return self._tool_history[-limit:]

    def get_session_summary(self) -> Dict[str, Any]:
        return {
            "session_id": self._session_id,
            "message_count": self._memory.message_count,
            "token_count": self._memory.token_count,
            "files_opened": list(self._file_context.keys()),
            "tool_count": len(self._tool_history),
            "unique_tools": list(set(t["tool"] for t in self._tool_history)),
        }


class OpenCodeIntegration:
    def __init__(self, storage=None):
        self._sessions: Dict[str, OpenCodeSession] = {}
        self._storage = storage

    def create_session(
        self,
        session_id: Optional[str] = None,
        max_tokens: int = 128000,
    ) -> OpenCodeSession:
        session = OpenCodeSession(
            session_id=session_id,
            max_tokens=max_tokens,
        )
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[OpenCodeSession]:
        return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def list_sessions(self) -> List[str]:
        return list(self._sessions.keys())
