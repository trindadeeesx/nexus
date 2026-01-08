# nexus/memory/store.py

from collections import deque
from datetime import datetime
from typing import Deque, Dict, List


class MemoryItem:
    def __init__(self, content: str, timestamp: datetime):
        self.content = content
        self.timestamp = timestamp


class ShortTermMemory:
    def __init__(self, max_items: int = 20):
        self.max_items = max_items
        self.items: Deque[MemoryItem] = deque(maxlen=max_items)

    def add(self, content: str):
        self.items.append(
            MemoryItem(
                content=content,
                timestamp=datetime.now(),
            )
        )

    def last(self, n: int = 3) -> List[str]:
        return [item.content for item in list(self.items)[-n:]]

    def clear(self):
        self.items.clear()


class MemoryStore:
    def __init__(self):
        self.by_source: Dict[str, ShortTermMemory] = {}

    def remember(self, source: str, text: str):
        if source not in self.by_source:
            self.by_source[source] = ShortTermMemory()
        self.by_source[source].add(text)

    def recall(self, source: str, n: int = 3) -> List[str]:
        if source not in self.by_source:
            return []
        return self.by_source[source].last(n)
