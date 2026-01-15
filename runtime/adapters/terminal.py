from cortex.contracts import ActionType
from runtime.adapters.base import RuntimeAdapter


class TerminalAdapter(RuntimeAdapter):
    name = "terminal"

    def send(self, action):
        if action.type == ActionType.SEND_MESSAGE:
            print(f"[{action.target.upper()}] {action.payload.get('text')}")
        elif action.type == ActionType.LOG:
            print(f"[LOG] {action.payload}")
