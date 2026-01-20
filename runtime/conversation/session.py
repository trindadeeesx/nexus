import time
from dataclasses import dataclass, field


@dataclass
class ConversationSession:
    session_id: str
    user_id: str
    stream: str
    agent: str
    state: str
    context: dict = field(default_factory=dict)
    last_activity: float = field(default_factory=time.time)
