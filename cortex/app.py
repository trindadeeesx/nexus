import uuid

from fastapi import FastAPI

from cortex.contracts import Event
from cortex.core import handle_event
from oracle.service import OracleService

app = FastAPI(title="Nexus Cortex")

ORACLE_SERVICE = OracleService()


@app.post("/event")
def receive_event(event: Event):
    if not event.id:
        event.id = str(uuid.uuid4())

    action = handle_event(event)

    return {
        "event_id": event.id,
        "action": action,
    }


@app.get("/oracle/metrics")
def oracle_metrics():
    metrics = ORACLE_SERVICE.metrics()
    return {
        "success_rate": metrics.success_rate(),
        "average_confidence": metrics.average_confidence(),
        "actions_count": dict(metrics.actions_count()),
    }


@app.get("/oracle/insights")
def oracle_insights():
    insights = ORACLE_SERVICE.analyze()
    return [
        {
            "ts": i.ts,
            "type": i.type,
            "source": i.source,
            "description": i.description,
            "confidence": i.confidence,
            "metadata": i.metadata,
        }
        for i in insights
    ]


@app.get("/oracle/history")
def oracle_history(limit: int = 100):
    history = ORACLE_SERVICE.storage.load(limit=limit)
    return [
        {
            "ts": r.ts,
            "event_type": r.event_type,
            "source": r.source,
            "action_type": r.action_type,
            "target": r.target,
            "confidence": r.confidence,
            "priority": r.priority,
            "result": r.result,
        }
        for r in history
    ]
