import uuid

from fastapi import APIRouter, Request
from pydantic import BaseModel

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
    metrics = request.app.state.oracle.metrics()
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


@router.get("/oracle/feedback")
def oracle_feedback(request: Request):
    actions = request.app.state.oracle.feedback()
    return [
        {
            "index": idx,
            "kind": fa.kind,
            "description": fa.description,
            "severity": fa.severity,
            "metadata": fa.metadata,
            "approved": None,  # inicialmente sem aprovação
        }
        for idx, fa in enumerate(actions)
    ]


class FeedbackApproval(BaseModel):
    index: int  # índice da ação na lista retornada
    approved: bool


@router.post("/oracle/feedback/approve")
def approve_feedback(request: Request, body: FeedbackApproval):
    """
    Aprova ou rejeita uma ação de feedback pelo índice
    """
    actions = request.app.state.oracle.feedback()
    if body.index < 0 or body.index >= len(actions):
        return {"error": "Índice inválido"}

    fa = actions[body.index]
    fa.approve(body.approved)

    return {
        "index": body.index,
        "approved": body.approved,
        "kind": fa.kind,
        "description": fa.description,
    }
