from agents.base import Agent
from cortex.contracts import Action, ActionType


class LuciaAgent(Agent):
    name = "lucia"

    def think(self, convo, session):
        text = convo.content.lower()

        if not session:
            return Action(
                type=ActionType.SEND_MESSAGE,
                target=convo.stream,
                payload={"text": "Olá! Como posso ajudar:"},
                confidence=0.9,
            )

        if "bolo" in text:
            session.context["topic"] = "bolo"
            return Action(
                type=ActionType.SEND_MESSAGE,
                target=convo.stream,
                payload={"text": "Que delícia 😄 Qual tipo de bolo você prefere?"},
                confidence=0.9,
            )

        if session.context.get("topic") == "bolo":
            return Action(
                type=ActionType.SEND_MESSAGE,
                target=convo.stream,
                payload={
                    "text": f"Perfeito! Vou te passar uma receita de bolo de {text} com cobertura 🍰"
                },
                confidence=0.95,
            )

        return Action.no_op("lucia_no_intent")

    def handle(self, action: Action) -> Action:
        if action.type == ActionType.SEND_MESSAGE:
            return Action(
                type=ActionType.SEND_MESSAGE,
                target=action.target,
                payload={"text": f"Lúcia diz: {action.payload.get('text')}"},
                confidence=0.9,
            )

        return action
