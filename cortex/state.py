import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


class GlobalState:
    def __init__(self):
        self.last_event_time: Optional[datetime] = None
        self.last_action_time: Optional[datetime] = None


SESSION_TIMEOUT_SECONDS = 30


@dataclass
class ConversationSession:
    session_id: str
    user_id: str
    stream: str
    agent: str  # lucia | dominus

    created_at: float
    last_activity: float
    state: str = "ACTIVE"  # ACTIVE | CLOSING | INACTIVE


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, ConversationSession] = {}

    def _make_key(self, user_id: str, stream: str) -> str:
        return f"{stream}:{user_id}"

    def get_session(self, user_id: str, stream: str) -> Optional[ConversationSession]:
        key = self._make_key(user_id, stream)
        session = self._sessions.get(key)

        if session and self.is_expired(session):
            self.close_session(session)
            return None

        return session

    def start_session(
        self, user_id: str, stream: str, agent: str
    ) -> ConversationSession:
        session = ConversationSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            stream=stream,
            agent=agent,
            created_at=time.time(),
            last_activity=time.time(),
        )

        self._sessions[self._make_key(user_id, stream)] = session
        return session

    def update_activity(self, session: ConversationSession):
        session.last_activity = time.time()

    def close_session(self, session: ConversationSession):
        session.state = "INACTIVE"
        key = self._make_key(session.user_id, session.stream)
        self._sessions.pop(key, None)

    def is_expired(self, session: ConversationSession) -> bool:
        return (time.time() - session.last_activity) > SESSION_TIMEOUT_SECONDS


STATE = GlobalState()
