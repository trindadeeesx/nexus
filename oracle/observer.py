from datetime import datetime
from typing import Any, Dict

from cortex.contracts import Action, Event
from oracle.models import ActionResult, OracleRecord
from oracle.storage import OracleStorage


class OracleObserver:
    def __init__(self, storage: OracleStorage):
        self.storage = storage

    def observe(
        self,
        event: Event,
        action: Action,
        result: ActionResult,
        metadata: Dict[str, Any] | None = None,
    ):
        record = OracleRecord(
            ts=datetime.now(),
            event_type=event.type,
            source=event.source,
            action_type=action.type,
            target=action.target,
            confidence=action.confidence,
            priority=action.priority,
            result=result,
            metadata=metadata,
        )

        self.storage.save(record)
        self._log(record)

    def _log(self, record: OracleRecord):
        print(
            f"[ORACLE] action={record.action_type} "
            f"result={record.result} "
            f"confidence={record.confidence}"
        )
