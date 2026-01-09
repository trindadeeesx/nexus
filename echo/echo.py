from cortex.contracts import Action, ActionType
from oracle.models import ActionResult


class Echo:
    def execute(self, action: Action) -> ActionResult:
        # simulação por tipo
        if action.type == ActionType.SEND_MESSAGE:
            return ActionResult.SUCCESS

        if action.type == ActionType.SPEAK:
            return ActionResult.IGNORED  # ainda não temos voz

        if action.type == ActionType.LOG:
            return ActionResult.SUCCESS

        return ActionResult.FAILED
