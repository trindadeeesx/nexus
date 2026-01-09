from oracle.analyzer import OracleAnalyzer
from oracle.feedback import FeedbackAction, OracleFeedback
from oracle.metrics import OracleMetrics
from oracle.observer import OracleObserver
from oracle.storage import OracleStorage


class OracleService:
    def __init__(self):
        self.storage = OracleStorage()
        self.observer = OracleObserver(self.storage)

    def observe(self, *args, **kwargs):
        self.observer.observe(*args, **kwargs)

    def analyze(self):
        history = self.storage.load()
        analyzer = OracleAnalyzer(history)
        return analyzer.analyze()

    def feedback(self):
        insights = self.analyze()
        feedback_procesor = OracleFeedback(insights)
        return feedback_procesor.process()

    def metrics(self):
        return OracleMetrics(self.storage.db_path)
