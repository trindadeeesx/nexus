from collections import Counter, defaultdict
from datetime import datetime, timedelta
from statistics import mean
from typing import List

from oracle.models import ActionResult, InsightType, OracleInsight, OracleRecord


class OracleAnalyzer:
    def __init__(self, history: list[OracleRecord]):
        self.history = history

    def analyze(self) -> list[OracleInsight]:
        insights: list[OracleInsight] = []

        insights.extend(self._detect_time_habits())
        insights.extend(self._detect_high_frequency())
        insights.extend(self._detect_low_confidence())
        insights.extend(self._detect_blocked_actions())
        insights.extend(self._detect_unused_policies())

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

    def _detect_high_frequency(self) -> List[OracleInsight]:
        insights = []

        recent = [
            r for r in self.history if r.ts >= datetime.now() - timedelta(minutes=10)
        ]

        counts = Counter((r.action_type, r.target) for r in recent)

        for (action, target), count in counts.items():
            if count >= 10:
                insights.append(
                    OracleInsight(
                        type=InsightType.ANOMALY,
                        source="oracle.analyzer",
                        description=(
                            f"Ação {action} para {target} "
                            f"executada {count} vezes em poucos minutos"
                        ),
                        confidence=0.8,
                        metadata={
                            "action_type": action,
                            "target": target,
                            "count": count,
                        },
                    )
                )

        return insights

    def _detect_low_confidence(self) -> List[OracleInsight]:
        insights = []

        grouped = defaultdict(list)

        for r in self.history:
            grouped[r.action_type].append(r.confidence)

        for action, confidences in grouped.items():
            if len(confidences) < 5:
                continue

            avg = sum(confidences) / len(confidences)

            if avg < 0.3:
                insights.append(
                    OracleInsight(
                        type=InsightType.SUGGESTION,
                        source="oracle.analyzer",
                        description=(
                            f"Ação {action} apresenta confiança média baixa ({avg:.2f})"
                        ),
                        confidence=1 - avg,
                        metadata={
                            "action_type": action,
                            "average_confidence": avg,
                        },
                    )
                )

        return insights

    def _detect_blocked_actions(self) -> List[OracleInsight]:
        insights = []

        total = len(self.history)
        if total == 0:
            return insights

        blocked = [
            r
            for r in self.history
            if r.result in (ActionResult.IGNORED, ActionResult.FAILED)
        ]

        rate = len(blocked) / total

        if rate >= 0.4:
            insights.append(
                OracleInsight(
                    type=InsightType.ANOMALY,
                    source="oracle.analyzer",
                    description=(f"Alta taxa de bloqueios detectada ({rate:.0%})"),
                    confidence=rate,
                    metadata={
                        "blocked": len(blocked),
                        "total": total,
                    },
                )
            )

        return insights

    def _detect_unused_policies(self) -> List[OracleInsight]:
        insights = []

        policies = defaultdict(list)

        for r in self.history:
            policy = r.metadata.get("policy")
            if policy:
                policies[policy].append(r.result)

        for policy, results in policies.items():
            success = sum(1 for r in results if r == ActionResult.SUCCESS)

            if success == 0 and len(results) >= 5:
                insights.append(
                    OracleInsight(
                        type=InsightType.SUGGESTION,
                        source="oracle.analyzer",
                        description=(
                            f"Policy '{policy}' nunca gerou ações bem-sucedidas"
                        ),
                        confidence=0.7,
                        metadata={
                            "policy": policy,
                            "attempts": len(results),
                        },
                    )
                )

        return insights
