from dataclasses import dataclass

from cortex.contracts import ConversationEvent
from cortex.decision import DecisionEngine


@dataclass
class Route:
    agent: str
    model_profile: str
    confidence: float = 0.5


class Router:
    def __init__(self, decision_engine: DecisionEngine):
        self.decision_engine = decision_engine

    def route(self, event: ConversationEvent) -> str:
        return self.decision_engine.decide_agent(event)
