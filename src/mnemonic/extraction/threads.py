from typing import List, Set
import re
from datetime import datetime

from mnemonic.core.models import OpenThread, MemoryItem


class OpenThreadDetector:
    def __init__(self):
        self._question_patterns = [
            r"(?:how|what|when|where|why|who|which|can|could|should|would|will|do|does)\s+[^.!?]+[?]",
            r"(?:i(?:'m)?|we(?:'re)?)\s+(?:not sure|unsure|confused|curious|wondering)\s+[^.!?]*[.?]",
            r"(?:need\s+to|have\s+to|should|would\s+like)\s+[^.!?]*\s+but\s+[^.!?]*[.?]",
            r"(?:still|yet)\s+(?:need|have|to)\s+[^.!?]*[.?]",
            r"(?:todo|to-do|tbd|to do|待办)",
        ]

        self._resolved_indicators = [
            "done",
            "completed",
            "finished",
            "resolved",
            "fixed",
            "solved",
            "implemented",
            "added",
            "created",
            "built",
            "done for now",
            "let's move on",
            "let's continue",
            "next",
            "moving on",
        ]

    def detect(self, messages: List[MemoryItem]) -> List[OpenThread]:
        threads = {}

        for idx, item in enumerate(messages):
            content = item.message.content

            questions = self._extract_questions(content)

            for question in questions:
                topic = self._extract_topic(question)

                if topic in threads:
                    thread = threads[topic]
                    thread.last_mentioned = item.message.timestamp
                else:
                    threads[topic] = OpenThread(
                        topic=topic,
                        question=question,
                        related_entities=self._extract_entities_from_question(question),
                        first_mentioned=item.message.timestamp,
                        last_mentioned=item.message.timestamp,
                    )

        resolved_topics = self._find_resolved_topics(messages)

        for topic in resolved_topics:
            if topic in threads:
                del threads[topic]

        return list(threads.values())

    def _extract_questions(self, content: str) -> List[str]:
        questions = []

        for pattern in self._question_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            questions.extend(matches)

        return questions

    def _extract_topic(self, question: str) -> str:
        question_lower = question.lower()

        words_to_remove = [
            "how do i",
            "how do we",
            "how can i",
            "how can we",
            "what is",
            "what are",
            "what's",
            "whats",
            "why is",
            "why are",
            "why does",
            "why did",
            "can i",
            "can we",
            "could i",
            "could we",
            "should i",
            "should we",
            "would be",
            "i'm not sure",
            "we're not sure",
            "i wonder",
            "i'm wondering",
            "do we",
            "does anyone",
            "has anyone",
        ]

        topic = question_lower
        for phrase in words_to_remove:
            topic = topic.replace(phrase, "")

        topic = re.sub(r"[^\w\s]", " ", topic)
        topic = " ".join(topic.split())

        if len(topic) > 50:
            topic = topic[:50] + "..."

        return topic.strip() or "general"

    def _extract_entities_from_question(self, question: str) -> List[str]:
        entities = []

        patterns = [
            r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b",
            r"\b\w+(?:\.\w+)+\b",
            r"\b\w+ing\b",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, question)
            entities.extend(matches[:3])

        return entities

    def _find_resolved_topics(self, messages: List[MemoryItem]) -> Set[str]:
        resolved = set()

        for item in messages:
            content_lower = item.message.content.lower()

            for indicator in self._resolved_indicators:
                if indicator in content_lower:
                    resolved.add(indicator)

        return resolved

    def mark_resolved(self, threads: List[OpenThread], topic: str) -> None:
        for thread in threads:
            if topic.lower() in thread.topic.lower():
                pass
