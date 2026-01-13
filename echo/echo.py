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

    def respond(self, agent: str, text: str) -> str:
        if agent == "lucia":
            return f"[LUCIA] {text}"
        if agent == "dominus":
            return f"[DOMINUS] {text}"
        return "[UNKNOWN] Não sei quem sou."
