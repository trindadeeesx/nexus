import uuid

from fastapi import APIRouter, Request

from cortex.contracts import Event
from cortex.core import handle_event

router = APIRouter()


@router.post("/event")
def receive_event(event: Event, request: Request):
    if not event.id:
        event.id = str(uuid.uuid4())

    action = handle_event(event)

    return {
        "event_id": event.id,
        "action": action,
    }


@router.get("/oracle/metrics")
def oracle_metrics(request: Request):
    metrics = request.app.state.oracle.oracle.metrics()
    return {
        "success_rate": metrics.success_rate(),
        "average_confidence": metrics.average_confidence(),
        "actions_count": dict(metrics.actions_count()),
    }


@router.get("/oracle/insights")
def oracle_insights(request: Request):
    insights = request.app.state.oracle.analyze()
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


@router.get("/oracle/history")
def oracle_history(request: Request, limit: int = 100):
    history = request.app.state.oracle.storage.load(limit=limit)
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
