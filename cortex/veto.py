from typing import Any, Dict

from cortex.classify import Intent
from cortex.contracts import Action


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
