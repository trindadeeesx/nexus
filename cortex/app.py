# nexus/cortex/app.py

import uuid
from enum import Enum
from typing import Any, Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from cortex.core import handle_event

app = FastAPI(title="Nexus Cortex")

# ========================
#   MODELS
# ========================


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


# ===================
#   HTTP
# ===================


@app.post("/event")
def receive_event(event: Event):
    if not event.id:
        event.id = str(uuid.uuid4())

    action = handle_event(event)

    return {
        "event_id": event.id,
        "action": action,
    }
