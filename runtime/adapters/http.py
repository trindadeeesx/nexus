from runtime.adapters.base import RuntimeAdapter


class HttpAdapter(RuntimeAdapter):
    name = "http"

    def send(self, action):
        # placeholder — no futuro FastAPI / WebSocket
        print(f"[HTTP OUT] {action.model_dump()}")
