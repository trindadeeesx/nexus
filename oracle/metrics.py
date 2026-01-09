import sqlite3
from collections import Counter
from pathlib import Path

from oracle.models import ActionResult


class OracleMetrics:
    def __init__(self, db_path: Path = Path("oracle.db")):
        self.db_path = db_path

    def success_rate(self) -> float:
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]

            if total == 0:
                return 0.0

            success = conn.execute(
                "SELECT COUNT(*) FROM observations WHERE result = ?",
                (ActionResult.SUCCESS,),
            ).fetchone()[0]

            return success / total

    def actions_count(self):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT action_type, COUNT(*) FROM observations GROUP BY action_type"
            ).fetchall()

        return Counter(dict(rows))

    def average_confidence(self) -> float:
        with sqlite3.connect(self.db_path) as conn:
            avg = conn.execute("SELECT AVG(confidence) FROM observations").fetchone()[0]

        return avg or 0.0
