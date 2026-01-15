from agents.base import Agent
from cortex.contracts import Action, ActionType


class LuciaAgent(Agent):
    name = "lucia"

    def handle(self, action: Action) -> Action:
        if action.type == ActionType.SEND_MESSAGE:
            return Action(
                type=ActionType.SEND_MESSAGE,
                target=action.target,
                payload={"text": f"Lúcia diz: {action.payload.get('text')}"},
                confidence=0.9,
            )

        return action
