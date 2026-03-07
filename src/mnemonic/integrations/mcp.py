from typing import List, Dict, Any, Optional
import json


class MCPServer:
    def __init__(self, memory):
        self._memory = memory
        self._tools = self._register_tools()

    def _register_tools(self) -> Dict[str, callable]:
        return {
            "get_context": self._get_context,
            "add_message": self._add_message,
            "get_recent_messages": self._get_recent_messages,
            "compact": self._compact,
            "get_session_info": self._get_session_info,
            "search_memory": self._search_memory,
        }

    def _get_context(
        self,
        query: str,
        max_tokens: Optional[int] = None,
    ) -> str:
        return self._memory.get_context_for(query, max_tokens)

    def _add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        item = self._memory.add_message(role, content, metadata)
        return {
            "id": item.id,
            "role": role,
            "content": content[:100] + "..." if len(content) > 100 else content,
            "token_count": item.message.token_count,
        }

    def _get_recent_messages(
        self,
        count: int = 10,
    ) -> List[Dict[str, Any]]:
        messages = self._memory.get_recent_messages(count)
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
            }
            for msg in messages
        ]

    def _compact(self) -> Dict[str, Any]:
        result = self._memory.compact()
        return {
            "original_count": result.original_count,
            "compacted_count": result.compacted_count,
            "tokens_saved": result.tokens_saved,
            "strategy_used": result.strategy_used,
        }

    def _get_session_info(self) -> Dict[str, Any]:
        return {
            "session_id": self._memory.session_id,
            "message_count": self._memory.message_count,
            "token_count": self._memory.token_count,
            "usage_ratio": self._memory.usage_ratio,
        }

    def _search_memory(
        self,
        query: str,
        max_results: int = 5,
    ) -> List[Dict[str, Any]]:
        context = self._memory.get_context_for(query, max_tokens=2000)

        return [
            {
                "content": context,
                "query": query,
            }
        ]

    def handle_request(
        self,
        tool: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        if tool not in self._tools:
            return {
                "error": f"Unknown tool: {tool}",
                "available_tools": list(self._tools.keys()),
            }

        try:
            result = self._tools[tool](**params)
            return {
                "success": True,
                "result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())

    def get_tool_schema(self, tool: str) -> Optional[Dict]:
        schemas = {
            "get_context": {
                "name": "get_context",
                "description": "Get relevant memory context for a query",
                "parameters": {
                    "query": {
                        "type": "string",
                        "description": "The query to find context for",
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Maximum tokens to return",
                    },
                },
            },
            "add_message": {
                "name": "add_message",
                "description": "Add a message to memory",
                "parameters": {
                    "role": {
                        "type": "string",
                        "description": "Role (user/assistant/system)",
                    },
                    "content": {"type": "string", "description": "Message content"},
                    "metadata": {"type": "object", "description": "Optional metadata"},
                },
            },
            "get_recent_messages": {
                "name": "get_recent_messages",
                "description": "Get recent messages from memory",
                "parameters": {
                    "count": {
                        "type": "integer",
                        "description": "Number of messages to return",
                    },
                },
            },
            "compact": {
                "name": "compact",
                "description": "Compact memory to stay within token limits",
                "parameters": {},
            },
            "get_session_info": {
                "name": "get_session_info",
                "description": "Get information about the current session",
                "parameters": {},
            },
            "search_memory": {
                "name": "search_memory",
                "description": "Search memory for relevant content",
                "parameters": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum results",
                    },
                },
            },
        }
        return schemas.get(tool)
