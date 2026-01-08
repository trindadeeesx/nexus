# nexus/cortex/app.py

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from memory.store import MemoryStore

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


# ========================
#   GLOBAL STATE
# ========================


class GlobalState:
    def __init__(self):
        self.last_event_time: Optional[datetime] = None
        self.last_action_time: Optional[datetime] = None


STATE = GlobalState()

# ========================
#   CLASSIFICATION
# ========================


class Intent(str, Enum):
    CHAT = "chat"
    COMMAND = "command"
    UNKNOWN = "unknown"


class Topic(str, Enum):
    FOOD = "food"
    WEATHER = "weather"
    SYSTEM = "system"
    RELATIONSHIP = "relationship"
    UNKNOWN = "unknown"


def classify_event(event: Event) -> Dict[str, Any]:
    text = event.payload.get("text", "").lower()

    intent = Intent.CHAT
    topic = Topic.UNKNOWN
    confidence = 0.5

    if any(word in text for word in ["ligar", "desligar", "abrir", "fechar"]):
        intent = Intent.COMMAND
        confidence = 0.8

    if any(word in text for word in ["bolo", "cookie", "comida", "receita", "torta"]):
        topic = Topic.FOOD
        confidence = 0.7

    if any(word in text for word in ["chuva", "clima", "tempo"]):
        topic = Topic.WEATHER
        confidence = 0.7

    if any(word in text for word in ["namorado", "namorada", "marido", "esposa"]):
        topic = Topic.RELATIONSHIP
        confidence = 0.7

    return {
        "intent": intent,
        "topic": topic,
        "confidence": confidence,
    }


# ========================
#   POLICIES
# ========================


class BasePolicy:
    name = "base"

    def applies(self, event: Event, classification: Dict[str, Any]) -> bool:
        return False

    def evaluate(self, event: Event, classification: Dict[str, Any]) -> List[Action]:
        return []


class ChatPolicy(BasePolicy):
    name = "chat_policy"

    def applies(self, event: Event, classification: Dict[str, Any]) -> bool:
        return classification["intent"] == Intent.CHAT

    def evaluate(self, event: Event, classification: Dict[str, Any]) -> List[Action]:
        return [
            Action(
                type=ActionType.SEND_MESSAGE,
                target=event.source,
                payload={"text": "Estou ouvindo."},
                priority=1,
                confidence=0.6,
            )
        ]


class FoodPolicy(BasePolicy):
    name = "food_policy"

    def applies(self, event: Event, classification: Dict[str, Any]) -> bool:
        return classification["topic"] == Topic.FOOD

    def evaluate(self, event: Event, classification: Dict[str, Any]) -> List[Action]:
        return [
            Action(
                type=ActionType.SEND_MESSAGE,
                target=event.source,
                payload={"text": "Posso sugerir uma receita se quiser."},
                priority=5,
                confidence=0.9,
            )
        ]


class PolicyEngine:
    def __init__(self, policies: List[BasePolicy]):
        self.policies = policies

    def run(self, event: Event, classification: Dict[str, Any]) -> List[Action]:
        actions: List[Action] = []

        for policy in self.policies:
            if policy.applies(event, classification):
                actions.extend(policy.evaluate(event, classification))

        return actions


POLICY_ENGINE = PolicyEngine(
    policies=[
        ChatPolicy(),
        FoodPolicy(),
    ]
)

# ========================
#   DECISION LAYER
# ========================


class DecisionLayer:
    def decide(self, actions: List[Action]) -> Optional[Action]:
        if not actions:
            return None

        actions = [a for a in actions if a.type != ActionType.NO_OP]

        if not actions:
            return None

        actions.sort(
            key=lambda a: (a.priority, a.confidence),
            reverse=True,
        )

        return actions[0]


DECISION_LAYER = DecisionLayer()

# ========================
#   GUARD LAYER
# ========================


class GuardResultReasons(str, Enum):
    CONFIDENCE_TOO_LOW = ("confidence_too_low",)
    COOLDOWN_ACTIVE = "cooldown_active"
    SILENT_HOURS = "silent_hours"


class GuardResult(BaseModel):
    allowed: bool
    reason: Optional[GuardResultReasons] = None


class Guard:
    MIN_CONFIDENCE = 0.6
    COOLDOWN_SECONDS = 5
    SILENT_HOURS = range(0, 7)

    def check(self, action: Action, state: GlobalState) -> GuardResult:
        now = datetime.now()

        if action.confidence < self.MIN_CONFIDENCE:
            return GuardResult(
                allowed=False, reason=GuardResultReasons.CONFIDENCE_TOO_LOW
            )

        if state.last_action_time:
            delta = (now - state.last_action_time).total_seconds()
            if delta < self.COOLDOWN_SECONDS:
                return GuardResult(
                    allowed=False, reason=GuardResultReasons.COOLDOWN_ACTIVE
                )

        if action.type == ActionType.SPEAK and now.hour in self.SILENT_HOURS:
            return GuardResult(
                allowed=False,
                reason=GuardResultReasons.SILENT_HOURS,
            )

        return GuardResult(allowed=True)


# ========================
#   VETO LAYER
# ========================


class VetoLayer:
    def veto(
        self,
        action: Action,
        classification: Dict[str, Any],
    ) -> bool:
        # exemplo: não interromper conversa casual
        if classification["intent"] == Intent.CHAT and action.priority < 5:
            return True

        return False


#
#   MEMORY
#


MEMORY = MemoryStore()

# ========================
#   CORTEX CORE
# ========================


def handle_event(event: Event) -> Action:
    STATE.last_event_time = datetime.now()

    text = event.payload.get("text")
    if text:
        MEMORY.remember(event.source, text)

    recent_context = MEMORY.recall(event.source)
    print(recent_context)

    classification = classify_event(event)

    proposed_actions = POLICY_ENGINE.run(event, classification)
    final_action = DECISION_LAYER.decide(proposed_actions)

    if not final_action:
        return Action(
            type=ActionType.LOG,
            target="system",
            payload={"info": "no action decided"},
        )

    guard = Guard()
    guard_result = guard.check(final_action, STATE)

    if not guard_result.allowed:
        return Action(
            type=ActionType.LOG,
            target="system",
            payload={"blocked_by": guard_result.reason},
        )

    veto = VetoLayer()
    if veto.veto(final_action, classification):
        return Action(
            type=ActionType.LOG,
            target="system",
            payload={"vetoed": True},
        )

    STATE.last_action_time = datetime.now()
    return final_action


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
