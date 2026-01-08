from typing import List, Optional

from cortex.app import Action, ActionType


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
