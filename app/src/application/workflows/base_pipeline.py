from abc import ABC, abstractmethod

from app.src.application.evaluators.result_evaluator import ResultEvaluator
from app.src.application.summary.summary_generator import SummaryGenerator


class BasePipeline(ABC):
    def __init__(self):
        self.evaluator = ResultEvaluator()
        self.summary_generator = SummaryGenerator()

    @abstractmethod
    def run(self, entity_list):
        """Execute the pipeline logic."""
        pass

    def finalize(self, dataset_processed):
        """Evaluate and summarize the pipeline results."""
        self.evaluator.evaluate_results(dataset_processed)
        summary = self.summary_generator.generate_summary(dataset_processed)
        print("\n=== Global Summary ===")
        print(summary)
        return dataset_processed
