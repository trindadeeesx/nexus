from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


class EventType(str, Enum):
    TEXT = "text"
    VOICE = "voice"
    SYSTEM = "system"


class ActionType(str, Enum):
    SEND_MESSAGE = "send_message"
    LOG = "log"
    SPEAK = "speak"
    NO_OP = "no_op"


class Event(BaseModel):
    id: Optional[str] = None
    type: EventType
    source: str
    payload: Dict[str, Any]


class Action(BaseModel):
    type: ActionType
    target: str
    payload: Dict[str, Any]
    confidence: float = 0.10
    priority: int = 0

    @classmethod
    def no_op(cls, reason: str | None = None) -> "Action":
        return cls(
            type=ActionType.NO_OP,
            target="system",
            payload={"reason": reason} if reason else {},
            confidence=0.0,
            priority=-1,
        )
