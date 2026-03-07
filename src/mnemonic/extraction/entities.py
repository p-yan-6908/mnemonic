from typing import List, Dict, Optional, Any
from datetime import datetime
import re

from mnemonic.core.models import Entity, MemoryItem
from mnemonic.core.exceptions import ExtractionError


class EntityExtractor:
    def __init__(self, entity_patterns: Optional[Dict[str, List[str]]] = None):
        self._patterns = entity_patterns or self._default_patterns()
        self._entity_types = {
            "protocol": [
                "oauth2",
                "http",
                "https",
                "websocket",
                "grpc",
                "rest",
                "graphql",
            ],
            "language": [
                "python",
                "javascript",
                "typescript",
                "go",
                "rust",
                "java",
                "c++",
            ],
            "framework": [
                "react",
                "vue",
                "angular",
                "django",
                "flask",
                "fastapi",
                "express",
            ],
            "library": ["pandas", "numpy", "requests", "axios", "lodash", "tiktoken"],
            "service": ["aws", "gcp", "azure", "heroku", "vercel", "netlify"],
            "tool": ["git", "docker", "kubernetes", "terraform", "ansible"],
            "concept": ["jwt", "oauth", "api", "cli", "sdk", "orm"],
        }

    def _default_patterns(self) -> Dict[str, List[str]]:
        return {
            " camelCase": r"\b[a-z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]*\b",
            " snake_case": r"\b[a-z][a-z0-9]*_[a-z0-9]+\b",
            " PascalCase": r"\b[A-Z][a-zA-Z0-9]+\b",
            " ALL_CAPS": r"\b[A-Z][A-Z0-9_]+\b",
            " version": r"\bv?\d+\.\d+\.\d+\b",
            " file_path": r"(?:\/[\w.-]+)+\.\w+",
            " url": r"https?://[^\s]+",
            " email": r"\b[\w.-]+@[\w.-]+\.\w+\b",
        }

    def extract(self, messages: List[MemoryItem]) -> Dict[str, Entity]:
        entities = {}

        for item in messages:
            content = item.message.content
            found = self._extract_from_content(content)

            for name, entity_type in found:
                if name in entities:
                    entity = entities[name]
                    entity.last_updated = datetime.utcnow()
                    entity.importance_score = max(
                        entity.importance_score, item.importance_score
                    )
                else:
                    entities[name] = Entity(
                        name=name,
                        entity_type=entity_type,
                        first_mentioned=item.message.timestamp,
                        last_updated=item.message.timestamp,
                        importance_score=item.importance_score,
                    )

        return entities

    def _extract_from_content(self, content: str) -> List[tuple]:
        found = []
        content_lower = content.lower()

        for entity_type, keywords in self._entity_types.items():
            for keyword in keywords:
                if keyword in content_lower:
                    found.append((keyword, entity_type))

        for pattern_name, pattern in self._patterns.items():
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) > 2:
                    entity_type = self._infer_type(match)
                    found.append((match, entity_type))

        return found

    def _infer_type(self, name: str) -> str:
        name_lower = name.lower()

        for entity_type, keywords in self._entity_types.items():
            if name_lower in keywords:
                return entity_type

        if "." in name:
            return "file"
        elif "/" in name or "\\" in name:
            return "path"
        elif name.isupper():
            return "constant"
        elif name[0].isupper() and name[0] == name[0]:
            return "class"
        else:
            return "identifier"

    def extract_with_llm(
        self, messages: List[MemoryItem], llm_client=None
    ) -> Dict[str, Entity]:
        if not llm_client:
            return self.extract(messages)

        raise NotImplementedError("LLM extraction not yet implemented")
