from collections import defaultdict
from statistics import mean

from oracle.models import InsightType, OracleInsight, OracleRecord


class OracleAnalyzer:
    def __init__(self, history: list[OracleRecord]):
        self.history = history

    def analyze(self) -> list[OracleInsight]:
        insights: list[OracleInsight] = []

        insights.extend(self._detect_time_habits())

        return insights

    def _detect_time_habits(self) -> list[OracleInsight]:
        by_source_action = defaultdict(list)

        for rec in self.history:
            key = (rec.source, rec.action_type)
            by_source_action[key].append(rec.ts)

        insights = []

        for (source, action), timestamps in by_source_action.items():
            if len(timestamps) < 5:
                continue

            hours = [ts.hour + ts.minute / 60 for ts in timestamps]
            avg_hour = mean(hours)
            variance = max(hours) - min(hours)

            if variance <= 0.5:  # ~ 30 minutos
                insights.append(
                    OracleInsight(
                        type=InsightType.HABIT,
                        source=source,
                        description=(
                            f"Ação {action} ocorre frequentemente "
                            f"por volta das {int(avg_hour)}h"
                        ),
                        confidence=0.8,
                        metadata={"avg_hour": avg_hour, "samples": len(hours)},
                    )
                )

        return insights
