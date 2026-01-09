from datetime import datetime
from enum import Enum
from typing import Any, Dict


class ActionResult(str, Enum):
    SUCCESS = "success"
    IGNORED = "ignored"
    FAILED = "failed"


class OracleRecord:
    def __init__(
        self,
        ts: datetime,
        event_type: str,
        source: str,
        action_type: str,
        target: str,
        confidence: float,
        priority: int,
        result: ActionResult,
        metadata: Dict[str, Any] | None = None,
    ):
        self.ts = ts
        self.event_type = event_type
        self.source = source
        self.action_type = action_type
        self.target = target
        self.confidence = confidence
        self.priority = priority
        self.result = result
        self.metadata = metadata or {}


class InsightType(str, Enum):
    HABIT = "habit"
    ANOMALY = "anomaly"
    SUGGESTION = "suggestion"


class OracleInsight:
    def __init__(
        self,
        type: InsightType,
        description: str,
        source: str | None = None,
        confidence: float = 0.5,
        severity: int = 1,  # 1=info, 2=warning, 3=critical
        metadata: Dict[str, Any] | None = None,
    ):
        self.ts = datetime.now()
        self.type = type
        self.source = source
        self.description = description
        self.confidence = confidence
        self.severity = severity
        self.metadata = metadata
