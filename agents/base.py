from cortex.contracts import Action


class Agent:
    name: str

    def handle(self, action: Action) -> Action:
        raise NotImplementedError
