from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from cortex.app import Action, ActionType, GlobalState


class GuardResultReasons(str, Enum):
    CONFIDENCE_TOO_LOW = ("confidence_too_low",)
    COOLDOWN_ACTIVE = "cooldown_active"
    SILENT_HOURS = "silent_hours"


class GuardResult(BaseModel):
    allowed: bool
    reason: Optional[GuardResultReasons] = None


class Guard:
    MIN_CONFIDENCE = 0.6
    COOLDOWN_SECONDS = 5
    SILENT_HOURS = range(0, 7)

    def check(self, action: Action, state: GlobalState) -> GuardResult:
        now = datetime.now()

        if action.confidence < self.MIN_CONFIDENCE:
            return GuardResult(
                allowed=False, reason=GuardResultReasons.CONFIDENCE_TOO_LOW
            )

        if state.last_action_time:
            delta = (now - state.last_action_time).total_seconds()
            if delta < self.COOLDOWN_SECONDS:
                return GuardResult(
                    allowed=False, reason=GuardResultReasons.COOLDOWN_ACTIVE
                )

        if action.type == ActionType.SPEAK and now.hour in self.SILENT_HOURS:
            return GuardResult(
                allowed=False,
                reason=GuardResultReasons.SILENT_HOURS,
            )

        return GuardResult(allowed=True)
