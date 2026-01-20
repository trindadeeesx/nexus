from agents.base import Agent
from cortex.contracts import Action, ActionType


class DominusAgent(Agent):
    name = "dominus"

    def think(self, convo, session):
        text = convo.content.lower()

        if "ligar computador" in text:
            return Action(
                type=ActionType.LOG,
                target="system",
                payload={"text": "Comando para ligar computador recebido"},
                confidence=0.95,
            )

        return Action.no_op("dominus_no_intent")
