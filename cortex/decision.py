from typing import List, Optional

from cortex.contracts import Action, ActionType, ConversationEvent
from cortex.state import SessionManager


class DecisionLayer:
    def decide(self, actions: List[Action]) -> Optional[Action]:
        if not actions:
            return None

        actions = [a for a in actions if a.type != ActionType.NO_OP]

        if not actions:
            return None

        actions.sort(
            key=lambda a: (a.priority, a.confidence),
            reverse=True,
        )

        return actions[0]


class DecisionEngine:
    def __init__(self, session_manager: SessionManager):
        self.sessions = session_manager

    def decide_agent(self, event: ConversationEvent) -> str:
        # 1 Existe sessão ativa?
        session = self.sessions.get_session(event.user_id, event.stream)

        if session:
            self.sessions.update_activity(session)
            event.session_id = session.session_id
            return session.agent

        # 2 Usuário chamou alguém explicitamente?
        if event.agent_hint:
            session = self.sessions.start_session(
                user_id=event.user_id,
                stream=event.stream,
                agent=event.agent_hint,
            )
            event.session_id = session.session_id
            return session.agent

        # 3 Nenhuma sessão, nenhum hint → fallback
        return "lucia"
