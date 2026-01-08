from typing import Any, Dict, List

from cortex.app import Action, ActionType, Event
from cortex.classify import Intent, Topic


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
