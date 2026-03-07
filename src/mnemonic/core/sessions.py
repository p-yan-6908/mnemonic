from typing import List, Optional, Dict
from datetime import datetime

from mnemonic.core.models import Session


class SessionManager:
    def __init__(self, storage):
        self._storage = storage

    def create_session(
        self,
        session_id: str,
        metadata: Optional[Dict] = None,
    ) -> Session:
        session = Session(
            id=session_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            messages=[],
            metadata=metadata or {},
        )

        self._storage.save_session(session)
        return session

    def get_or_create_session(
        self,
        session_id: str,
        metadata: Optional[Dict] = None,
    ) -> Session:
        session = self._storage.get_session(session_id)

        if session is None:
            session = self.create_session(session_id, metadata)

        return session

    def list_user_sessions(
        self,
        user_id: str,
        limit: int = 100,
    ) -> List[Session]:
        all_sessions = self._storage.list_sessions(limit * 2)

        user_sessions = [
            s for s in all_sessions if s.metadata.get("user_id") == user_id
        ]

        return user_sessions[:limit]

    def delete_session(self, session_id: str) -> bool:
        session = self._storage.get_session(session_id)

        if session is None:
            return False

        for item in session.messages:
            self._storage.delete(item.id)

        return True


class SharedMemorySpace:
    def __init__(
        self,
        space_id: str,
        storage,
        agent_ids: Optional[List[str]] = None,
    ):
        self._space_id = space_id
        self._storage = storage
        self._agent_ids = agent_ids or []
        self._shared_entities: Dict[str, Dict] = {}
        self._shared_decisions: List[Dict] = []

    @property
    def space_id(self) -> str:
        return self._space_id

    def add_agent(self, agent_id: str) -> None:
        if agent_id not in self._agent_ids:
            self._agent_ids.append(agent_id)

    def remove_agent(self, agent_id: str) -> bool:
        if agent_id in self._agent_ids:
            self._agent_ids.remove(agent_id)
            return True
        return False

    def get_agents(self) -> List[str]:
        return self._agent_ids.copy()

    def store_shared_entity(
        self,
        name: str,
        entity_type: str,
        attributes: Optional[Dict] = None,
    ) -> None:
        self._shared_entities[name] = {
            "type": entity_type,
            "attributes": attributes or {},
            "updated_at": datetime.utcnow().isoformat(),
        }

    def get_shared_entity(self, name: str) -> Optional[Dict]:
        return self._shared_entities.get(name)

    def get_all_shared_entities(self) -> Dict[str, Dict]:
        return self._shared_entities.copy()

    def add_shared_decision(
        self,
        decision: str,
        participants: List[str],
    ) -> None:
        self._shared_decisions.append(
            {
                "statement": decision,
                "participants": participants,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def get_shared_decisions(self) -> List[Dict]:
        return self._shared_decisions.copy()

    def clear(self) -> None:
        self._shared_entities.clear()
        self._shared_decisions.clear()


class MultiAgentCoordinator:
    def __init__(self, storage):
        self._storage = storage
        self._spaces: Dict[str, SharedMemorySpace] = {}
        self._session_manager = SessionManager(storage)

    def create_shared_space(
        self,
        space_id: str,
        agent_ids: Optional[List[str]] = None,
    ) -> SharedMemorySpace:
        space = SharedMemorySpace(space_id, self._storage, agent_ids)
        self._spaces[space_id] = space
        return space

    def get_shared_space(self, space_id: str) -> Optional[SharedMemorySpace]:
        return self._spaces.get(space_id)

    def delete_shared_space(self, space_id: str) -> bool:
        if space_id in self._spaces:
            del self._spaces[space_id]
            return True
        return False

    def list_shared_spaces(self) -> List[str]:
        return list(self._spaces.keys())
