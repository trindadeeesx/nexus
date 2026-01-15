import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass
class Session:
    session_id: str
    user_id: str
    stream: str
    agent: str
    state: str = "IDLE"
    last_activity: float = field(default_factory=time.time)


@dataclass
class GlobalState:
    last_action_time: Optional[datetime] = None


class SessionManager:
    TIMEOUT_SECONDS = 120

    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    def _key(self, user_id: str, stream: str) -> str:
        return f"{stream}:{user_id}"

    def get_session(self, user_id: str, stream: str) -> Optional[Session]:
        key = self._key(user_id, stream)
        session = self.sessions.get(key)

        if not session:
            return None

        if time.time() - session.last_activity > self.TIMEOUT_SECONDS:
            del self.sessions[key]
            return None

        return session

    def start_session(self, user_id: str, stream: str, agent: str) -> Session:
        session = Session(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            stream=stream,
            agent=agent,
            state="IN_CONVERSATION",
        )
        self.sessions[self._key(user_id, stream)] = session
        return session

    def update_activity(self, session: Session):
        session.last_activity = time.time()

    def close(self, session: Session):
        key = self._key(session.user_id, session.stream)
        if key in self.sessions:
            del self.sessions[key]
