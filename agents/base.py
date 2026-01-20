from typing import Optional

from cortex.contracts import Action, ConversationEvent


class Agent:
    name: str

    def think(
        self, convo: ConversationEvent, session: Optional[object]
    ) -> Optional[Action]:
        raise NotImplementedError

    def handle(self, action: Action) -> Action:
        raise action
