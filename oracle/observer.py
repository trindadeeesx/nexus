from datetime import datetime
from enum import Enum
from typing import Any, Dict

from cortex.contracts import Action, Event


class ActionResult(str, Enum):
    SUCCESS = "success"
    IGNORED = "ignored"
    FAILED = "failed"


class Oracle:
    def __init__(self):
        self.history = []

    def observe(
        self,
        event: Event,
        action: Action,
        result: ActionResult,
        metadata: Dict[str, Any] | None = None,
    ):
        record = {
            "ts": datetime.now(),
            "event": event.type,
            "source": event.source,
            "action": action.type,
            "target": action.target,
            "confidence": action.confidence,
            "priority": action.priority,
            "result": result,
            "meta": metadata or {},
        }

        self.history.append(record)
        self._learn(record)

    def _learn(self, record: Dict[str, Any]):
        print(
            "[ORACLE]",
            record["action"],
            record["result"],
            record["confidence"],
        )
