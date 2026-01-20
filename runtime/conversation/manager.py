from uuid import uuid4

from runtime.conversation.session import ConversationSession


class ConversationManager:
    def __init__(self):
        self.sessions = {}

    def get(self, user_id, stream):
        return self.sessions.get(f"{stream}:{user_id}")

    def start(self, user_id, stream, agent):
        session = ConversationSession(
            session_id=str(uuid4()),
            user_id=user_id,
            stream=stream,
            agent=agent,
            state="IN_CONVERSATION",
        )

        self.sessions[f"{stream}:{user_id}"] = session
        return session

    def close(self, user_id, stream):
        self.sessions.pop(f"{stream}:{user_id}", None)
