from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from cortex.contracts import Action, ActionType, Event, EventType
from cortex.state import GlobalState


class GuardResultReasons(str, Enum):
    CONFIDENCE_TOO_LOW = ("confidence_too_low",)
    COOLDOWN_ACTIVE = "cooldown_active"
    SILENT_HOURS = "silent_hours"
    VOICE_WITHOUT_HOTWORD = "voice_without_hotword"


class GuardResult(BaseModel):
    allowed: bool
    reason: Optional[GuardResultReasons] = None


class Guard:
    MIN_CONFIDENCE = 0.6
    COOLDOWN_SECONDS = 5
    SILENT_HOURS = range(0, 7)

    def check(
        self, action: Action, state: GlobalState, event: Event | None = None
    ) -> GuardResult:
        now = datetime.now()

        if event and event.type == EventType.VOICE:
            if not event.payload.get("invoked_by_hotword"):
                return GuardResult(
                    allowed=False, reason=GuardResultReasons.VOICE_WITHOUT_HOTWORD
                )

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
