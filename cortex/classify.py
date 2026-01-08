from enum import Enum
from typing import Any, Dict

from cortex.contracts import Event


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
