import uuid

from fastapi import FastAPI

from cortex.contracts import Event
from cortex.core import handle_event

app = FastAPI(title="Nexus Cortex")

# ===================
#   HTTP
# ===================


@app.post("/event")
def receive_event(event: Event):
    if not event.id:
        event.id = str(uuid.uuid4())

    action = handle_event(event)

    return {
        "event_id": event.id,
        "action": action,
    }
