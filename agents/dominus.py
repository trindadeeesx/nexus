from agents.base import Agent
from cortex.contracts import Action, ActionType


class DominusAgent(Agent):
    name = "dominus"

    def handle(self, action: Action) -> Action:
        if action.type == ActionType.SEND_MESSAGE:
            return Action(
                type=ActionType.SEND_MESSAGE,
                target=action.target,
                payload={"text": f"Dominus executou: {action.payload.get('text')}"},
                confidence=0.95,
            )

        return action
