from typing import List, Optional
import re
from datetime import datetime

from mnemonic.core.models import Decision, MemoryItem


class DecisionTracker:
    def __init__(self):
        self._decision_patterns = [
            r"(?:we(?:'ve)?|I(?:'ve)?)?\s*(?:decided|agreed|chose|selected|picked)\s+(?:to\s+)?(.+)",
            r"(?:the\s+)?(?:decision|choice)\s+(?:is|was|to)\s+(.+)",
            r"(?:let(?:'s)?|let us)\s+(?:go\s+with|use|implement)\s+(.+)",
            r"(?:we(?:'ll)?|I(?: will)?)\s+(?:use|implement|build|create)\s+(.+)",
            r"(?:going\s+with|stick\s+with|proceed\s+with)\s+(.+)",
            r"(?:best\s+(?:choice|option|approach|solution))\s+(?:is|to)\s+(.+)",
            r"(?:use|adopt|employ)\s+(?:the\s+)?(.+?)\s+(?:for|as|instead)",
        ]

    def extract(self, messages: List[MemoryItem]) -> List[Decision]:
        decisions = []

        for item in messages:
            content = item.message.content

            found_decisions = self._extract_from_content(content, item)

            for decision_text in found_decisions:
                decisions.append(
                    Decision(
                        statement=decision_text.strip(),
                        timestamp=item.message.timestamp,
                        participants=[
                            "user" if item.message.role == "user" else "assistant"
                        ],
                        status="active",
                    )
                )

        return decisions

    def _extract_from_content(self, content: str, item: MemoryItem) -> List[str]:
        decisions = []

        for pattern in self._decision_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            decisions.extend(matches)

        if any(kw in content.lower() for kw in ["decided", "agreed", "decision"]):
            sentences = re.split(r"[.!?]", content)
            for sentence in sentences:
                if any(
                    kw in sentence.lower() for kw in ["decided", "agreed", "decision"]
                ):
                    if len(sentence.strip()) > 10:
                        decisions.append(sentence.strip())

        unique_decisions = []
        seen = set()
        for d in decisions:
            d_lower = d.lower().strip()
            if d_lower not in seen and len(d_lower) > 5:
                seen.add(d_lower)
                unique_decisions.append(d)

        return unique_decisions

    def find_decisions_for_entity(
        self, decisions: List[Decision], entity_name: str
    ) -> List[Decision]:
        entity_lower = entity_name.lower()
        return [d for d in decisions if entity_lower in d.statement.lower()]

    def mark_resolved(self, decisions: List[Decision], decision_text: str) -> None:
        for d in decisions:
            if decision_text.lower() in d.statement.lower():
                d.status = "resolved"
