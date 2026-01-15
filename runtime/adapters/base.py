class RuntimeAdapter:
    name: str

    def send(self, action):
        raise NotImplementedError
