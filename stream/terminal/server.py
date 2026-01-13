import socket
import threading

from cortex.contracts import ConversationEvent
from cortex.decision import DecisionEngine
from cortex.state import SessionManager
from echo.echo import Echo

ECHO = Echo()

HOST = "127.0.0.1"
PORT = 8765


class TerminalStreamServer:
    def __init__(self):
        self.sessions = SessionManager()
        self.decision = DecisionEngine(self.sessions)

    def handle_client(self, conn: socket.socket, addr):
        user_id = f"terminal:{addr[1]}"

        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break

                text = data.decode().strip()
                if not text:
                    continue

                event = ConversationEvent(
                    stream="terminal",
                    user_id=user_id,
                    agent_hint=self.extract_agent_hint(text),
                    content=text,
                )

                agent = self.decision.decide_agent(event)
                reply = ECHO.respond(agent, text)
                print("agent:", agent, "text:", text)
                print("reply:", reply)

                conn.sendall((reply + "\n").encode())

        finally:
            conn.close()

    @staticmethod
    def extract_agent_hint(text: str):
        lowered = text.lower()
        if lowered.startswith("lucia"):
            return "lucia"
        if lowered.startswith("dominus"):
            return "dominus"
        return None

    def serve(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()

            print(f"[TerminalStream] Escutando em {HOST}:{PORT}")

            while True:
                conn, addr = s.accept()
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr),
                    daemon=True,
                )
                thread.start()


def main():
    server = TerminalStreamServer()
    server.serve()


if __name__ == "__main__":
    main()
