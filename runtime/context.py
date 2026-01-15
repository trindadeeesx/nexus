from typing import Dict

from cortex.contracts import ConversationEvent
from cortex.state import SessionManager
from memory.store import MemoryStore
from oracle.service import OracleService


class NexusContext:
    def __init__(self):
        self.session_manager = SessionManager()
        self.memory = MemoryStore()
        self.oracle = OracleService()

        # registry
        self.adapters: Dict[str, object] = {}
        self.agents: Dict[str, object] = {}
        self.models: Dict[str, object] = {}

    def register_adapter(self, name: str, adapter):
        self.adapters[name] = adapter

    def register_agent(self, name: str, agent):
        self.agents[name] = agent

    def register_model(self, name: str, model):
        self.models[name] = model

    def build_conversation_event(
        self,
        *,
        text: str,
        user_id: str,
        stream: str,
        modality: str = "text",
        agent_hint: str | None = None,
        metadata: dict | None = None,
    ) -> ConversationEvent:
        session = self.session_manager.get_session(user_id, stream)

        return ConversationEvent(
            stream=stream,
            user_id=user_id,
            session_id=session.session_id if session else None,
            agent_hint=agent_hint,
            modality=modality,
            content=text,
            metadata=metadata or {},
        )
