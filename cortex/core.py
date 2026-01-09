from datetime import datetime

from cortex.classify import classify_event
from cortex.contracts import (  # models continuam no app por enquanto
    Action,
    ActionType,
    Event,
)
from cortex.decision import DecisionLayer
from cortex.policies import ChatPolicy, FoodPolicy, PolicyEngine
from cortex.state import STATE
from cortex.veto import VetoLayer
from echo.echo import Echo
from guard.guard import Guard
from memory.store import MemoryStore
from oracle.observer import ActionResult
from oracle.service import OracleService

# ========================
#   ENGINES SINGLETONS
# ========================

POLICY_ENGINE = PolicyEngine(
    policies=[
        ChatPolicy(),
        FoodPolicy(),
    ]
)

DECISION_LAYER = DecisionLayer()
MEMORY = MemoryStore()

ORACLE = OracleService()
ECHO = Echo()

# ========================
#   CORE ORCHESTRATION
# ========================


def handle_event(event: Event) -> Action:
    STATE.last_event_time = datetime.now()

    # ---- Memory ----
    text = event.payload.get("text")
    if text:
        MEMORY.remember(event.source, text)

    recent_context = MEMORY.recall(event.source)
    # futuramente isso entra no prompt / contexto
    # print(recent_context)

    # ---- Classification ----
    classification = classify_event(event)

    # ---- Policies ----
    proposed_actions = POLICY_ENGINE.run(event, classification)

    # ---- Decision ----
    final_action = DECISION_LAYER.decide(proposed_actions)

    if not final_action:
        ORACLE.observe(
            event=event,
            action=Action.no_op("no_action"),
            result=ActionResult.IGNORED,
            metadata={"reason": "no_action"},
        )

        return Action(
            type=ActionType.LOG,
            target="system",
            payload={"info": "no action decided"},
        )

    # ---- Guard ----
    guard = Guard()
    guard_result = guard.check(final_action, STATE)

    if not guard_result.allowed:
        return Action(
            type=ActionType.LOG,
            target="system",
            payload={"blocked_by": guard_result.reason},
        )

    # ---- Veto ----
    veto = VetoLayer()
    if veto.veto(final_action, classification):
        ORACLE.observe(
            event=event,
            action=final_action,
            result=ActionResult.IGNORED,
            metadata={"reason": "veto"},
        )

        return Action(
            type=ActionType.LOG,
            target="system",
            payload={"vetoed": True},
        )

    STATE.last_action_time = datetime.now()

    result = ECHO.execute(final_action)

    ORACLE.observe(
        event=event,
        action=final_action,
        result=result,  # por enquanto sempre sucesso
    )
    return final_action
