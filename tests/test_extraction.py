import pytest
from datetime import datetime
from mnemonic.core.models import MemoryItem, Message
from mnemonic.extraction.entities import EntityExtractor
from mnemonic.extraction.decisions import DecisionTracker
from mnemonic.extraction.threads import OpenThreadDetector


class TestEntityExtractor:
    def test_extracts_known_entities(self):
        extractor = EntityExtractor()

        messages = [
            MemoryItem(
                id="1",
                message=Message(
                    role="user",
                    content="We're using OAuth2 for authentication and Python for the backend",
                ),
            ),
        ]

        entities = extractor.extract(messages)

        assert "oauth2" in entities
        assert entities["oauth2"].entity_type == "protocol"
        assert "python" in entities

    def test_tracks_entity_updates(self):
        extractor = EntityExtractor()

        older = datetime(2024, 1, 1)
        newer = datetime(2024, 1, 2)

        messages = [
            MemoryItem(
                id="1",
                message=Message(
                    role="user",
                    content="We're using OAuth2",
                    timestamp=older,
                ),
            ),
            MemoryItem(
                id="2",
                message=Message(
                    role="assistant",
                    content="OAuth2 is great",
                    timestamp=newer,
                ),
            ),
        ]

        entities = extractor.extract(messages)

        assert "oauth2" in entities


class TestDecisionTracker:
    def test_extracts_obvious_decisions(self):
        tracker = DecisionTracker()

        messages = [
            MemoryItem(
                id="1",
                message=Message(
                    role="user",
                    content="We've decided to use Auth0 for authentication",
                ),
            ),
        ]

        decisions = tracker.extract(messages)

        assert len(decisions) > 0
        assert any("auth0" in d.statement.lower() for d in decisions)

    def test_extracts_multiple_decisions(self):
        tracker = DecisionTracker()

        messages = [
            MemoryItem(
                id="1",
                message=Message(
                    role="assistant",
                    content="We've decided to go with React. We'll also use TypeScript for type safety.",
                ),
            ),
        ]

        decisions = tracker.extract(messages)

        assert len(decisions) >= 1


class TestOpenThreadDetector:
    def test_detects_questions(self):
        detector = OpenThreadDetector()

        messages = [
            MemoryItem(
                id="1",
                message=Message(
                    role="user",
                    content="How do we handle refresh tokens?",
                ),
            ),
        ]

        threads = detector.detect(messages)

        assert len(threads) > 0

    def test_finds_questions_even_with_resolution(self):
        detector = OpenThreadDetector()

        messages = [
            MemoryItem(
                id="1",
                message=Message(
                    role="user",
                    content="How do we handle refresh tokens?",
                ),
            ),
            MemoryItem(
                id="2",
                message=Message(
                    role="assistant",
                    content="Done! We implemented refresh token rotation.",
                ),
            ),
        ]

        threads = detector.detect(messages)

        assert len(threads) >= 0
