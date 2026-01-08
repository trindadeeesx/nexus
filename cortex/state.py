from datetime import datetime
from typing import Optional


class GlobalState:
    def __init__(self):
        self.last_event_time: Optional[datetime] = None
        self.last_action_time: Optional[datetime] = None


STATE = GlobalState()
