import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List

from oracle.models import OracleRecord
from oracle.observer import ActionResult


class OracleStorage:
    def __init__(self, path: str = "oracle.db"):
        self.db_path = Path(path)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT,
                    event_type TEXT,
                    source TEXT,
                    action_type TEXT,
                    target TEXT,
                    confidence REAL,
                    priority INTEGER,
                    result TEXT
                )
                """
            )

    def save(self, rec: OracleRecord):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO observations (
                    ts, event_type, source, action_type,
                    target, confidence, priority, result
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rec.ts.isoformat(),
                    rec.event_type,
                    rec.source,
                    rec.action_type,
                    rec.target,
                    rec.confidence,
                    rec.priority,
                    rec.result,
                ),
            )

    def load(self, limit: int | None = None) -> List[OracleRecord]:
        query = """
                SELECT
                    ts, event_type, source, action_type,
                    target, confidence, priority, result
                FROM observations
                ORDER BY ts ASC
            """

        if limit:
            query += f" LIMIT {limit}"

        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(query).fetchall()

        recs: List[OracleRecord] = []

        for row in rows:
            recs.append(
                OracleRecord(
                    ts=datetime.fromisoformat(row[0]),
                    event_type=row[1],
                    source=row[2],
                    action_type=row[3],
                    target=row[4],
                    confidence=row[5],
                    priority=row[6],
                    result=ActionResult(row[7]),
                )
            )

        return recs
