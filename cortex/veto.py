from typing import Any, Dict

from cortex.app import Action
from cortex.classify import Intent


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
