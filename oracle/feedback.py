from collections import defaultdict
from typing import Dict, List

from oracle.models import InsightType, OracleInsight


class FeedbackAction:
    def __init__(
        self, kind: str, description: str, severity: int, metadata: Dict | None = None
    ):
        self.kind = kind  # log | notify | suggest | adjust | ask_user
        self.description = description
        self.severity = severity
        self.metadata = metadata or {}
        self.confidence = self.metadata.get("confidence", 0.5)

        self.approved: bool | None = None

    def approve(self, approved: bool):
        self.approved = approved


class OracleFeedback:
    def __init__(self, insights: List[OracleInsight]):
        self.insights = insights

    def process(self) -> List[FeedbackAction]:
        actions: List[FeedbackAction] = []

        for insight in self.insights:
            if insight.type == InsightType.HABIT:
                actions.append(self._handle_habit(insight))

            elif insight.type == InsightType.SUGGESTION:
                actions.append(self._handle_suggestion(insight))

            elif insight.type == InsightType.ANOMALY:
                actions.append(self._handle_anomaly(insight))

        return [a for a in actions if a is not None]

    def _handle_habit(self, insight: OracleInsight) -> FeedbackAction:
        return FeedbackAction(
            kind="suggest",
            description=(
                "Padrão recorrente detectado. Pode virar rotina automática no futuro."
            ),
            severity=insight.severity,
            metadata=insight.metadata,
        )

    def _handle_suggestion(self, insight: OracleInsight) -> FeedbackAction:
        if insight.confidence >= 0.7:
            return FeedbackAction(
                kind="suggest",
                description=insight.description,
                severity=insight.severity,
                metadata=insight.metadata,
            )

        return FeedbackAction(
            kind="log",
            description=f"Sugestão ignorada por baixa confiança: {insight.description}",
            severity=1,
        )

    def _handle_anomaly(self, insight: OracleInsight) -> FeedbackAction:
        if insight.severity >= 3:
            return FeedbackAction(
                kind="notify",
                description=f"Anomalia crítica: {insight.description}",
                severity=insight.severity,
                metadata=insight.metadata,
            )

        return FeedbackAction(
            kind="log",
            description=f"Anomalia detectada: {insight.description}",
            severity=insight.severity,
            metadata=insight.metadata,
        )
