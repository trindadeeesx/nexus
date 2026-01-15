from datetime import datetime
from typing import Any, Dict

from cortex.classify import classify_event
from cortex.contracts import ActionType, Event, EventType
from cortex.decision import DecisionEngine, DecisionLayer
from cortex.policies import ChatPolicy, FoodPolicy, PolicyEngine
from cortex.state import GlobalState, SessionManager
from cortex.veto import VetoLayer
from echo.echo import Echo
from guard.guard import Guard
from memory.store import MemoryStore
from oracle.service import OracleService
from runtime.router import Router


class NexusRuntime:
    def __init__(self, ctx):
        self.ctx = ctx

        self.sessions = SessionManager()
        self.memory = MemoryStore()
        self.global_state = GlobalState()

        self.policy_engine = PolicyEngine(
            [
                FoodPolicy(),
                ChatPolicy(),
            ]
        )

        self.decision_layer = DecisionLayer()
        self.decision_engine = DecisionEngine(self.sessions)
        self.router = Router(self.decision_engine)

        self.veto = VetoLayer()
        self.guard = Guard()
        self.echo = Echo()
        self.oracle = OracleService()

    def handle_input(
        self,
        text: str,
        user_id: str,
        stream: str,
    ) -> Dict[str, Any]:
        # 1. Criar evento
        event = Event(
            type=EventType.TEXT,
            source=stream,
            payload={"text": text},
        )

        convo = self.ctx.build_conversation_event(
            text=text,
            user_id=user_id,
            stream=stream,
        )

        # 2. Roteamento
        agent = self.router.route(convo)

        # 3. Classificação
        classification = classify_event(event)

        # 4. Políticas
        actions = self.policy_engine.run(event, classification)

        # 5. Decisão
        action = self.decision_layer.decide(actions)
        if not action:
            return {"agent": agent, "action": None}

        # 6. Veto
        if self.veto.veto(action, classification):
            self.oracle.observe(event, action, "IGNORED", {"vetoed": True})
            return {"agent": agent, "action": None}

        # 7. Guard
        guard_result = self.guard.check(action, self.ctx.global_state, event)
        if not guard_result.allowed:
            self.oracle.observe(
                event, action, "BLOCKED", {"reason": guard_result.reason}
            )
            return {"agent": agent, "action": None}

        # 8. Execução
        result = self.echo.execute(action)

        # Atualiza estado global
        self.global_state.last_action_time = datetime.now()

        # Oracle
        self.oracle.observe(event, action, result)

        # 9. Oracle
        self.oracle.observe(event, action, result)

        # 10. Memória
        if action.type == ActionType.SEND_MESSAGE:
            self.memory.remember(stream, action.payload.get("text", ""))

        return {
            "agent": agent,
            "action": action.dict(),
            "result": result,
        }
