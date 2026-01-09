import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from cortex.contracts import Action, ActionType, Event, EventType
from oracle.models import ActionResult
from oracle.service import OracleService

# -----------------------------
# Setup
# -----------------------------
oracle = OracleService()

# -----------------------------
# Criar eventos falsos
# -----------------------------
sources = ["Vinicius", "Ana Paula", "Luiz"]
actions = ["open_window", "close_window", "make_coffee", "turn_on_light"]
targets = ["quarto", "cozinha", "sala"]

# Limpar histórico para teste (opcional, se quiser um ambiente limpo)
oracle.storage.db_path.unlink(missing_ok=True)
oracle.storage._init_db()

for i in range(50):
    event = Event(
        id=str(i),
        type=EventType.SYSTEM,
        source=random.choice(sources),
        payload={"text": f"Evento de teste {i}"},
    )

    action_type = random.choice(actions)
    target = random.choice(targets)
    action = Action(
        type=ActionType.SEND_MESSAGE,
        target=target,
        payload={"info": f"Ação simulada {i}"},
        confidence=random.uniform(0.2, 1.0),
        priority=random.randint(1, 5),
    )

    result = random.choices(
        [ActionResult.SUCCESS, ActionResult.FAILED, ActionResult.IGNORED],
        weights=[0.7, 0.2, 0.1],
    )[0]

    oracle.observe(event, action, result, metadata={"policy": f"policy_{i % 3}"})

# -----------------------------
# Analisar e gerar insights
# -----------------------------
insights = oracle.analyze()
print(f"\n=== {len(insights)} Insights Gerados ===")
for i in insights:
    print(
        f"[{i.type}] {i.description} (conf={i.confidence:.2f}, severity={i.severity})"
    )

# -----------------------------
# Processar feedback
# -----------------------------
feedback_actions = oracle.feedback()
print(f"\n=== {len(feedback_actions)} Feedback Actions ===")
for fa in feedback_actions:
    # Aprovar algumas ações aleatoriamente para simular o loop
    fa.approve(True)

    print(
        f"[{fa.kind}] {fa.description} (severity={fa.severity}, metadata={fa.metadata})"
    )
