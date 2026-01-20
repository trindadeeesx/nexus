from enum import Enum


class ConversationState(str, Enum):
    IDLE = "idle"
    AWAITING_REPLY = "awaiting_reply"
    IN_TASK = "in_task"
    CLOSED = "closed"
