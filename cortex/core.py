from datetime import datetime

from cortex.app import Action, ActionType, Event  # models continuam no app por enquanto
from cortex.classify import classify_event
from cortex.decision import DecisionLayer
from cortex.policies import ChatPolicy, FoodPolicy, PolicyEngine
from cortex.state import STATE
from cortex.veto import VetoLayer
from guard.guard import Guard
from memory.store import MemoryStore

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
        return Action(
            type=ActionType.LOG,
            target="system",
            payload={"vetoed": True},
        )

    STATE.last_action_time = datetime.now()
    return final_action
