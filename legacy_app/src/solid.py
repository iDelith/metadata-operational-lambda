import json
from abc import ABC, abstractmethod
from typing import Dict, List

# ==================================
#  Domain Interfaces (Abstractions)
# ==================================


class ITableProcessor(ABC):
    @abstractmethod
    def process_table(self, db_name: str, table_name: str) -> Dict[str, str]:
        pass


class IDatabaseProcessor(ABC):
    @abstractmethod
    def process_databases(self, entity_list: Dict[str, List[str]]) -> Dict[str, Dict]:
        pass


class IResultEvaluator(ABC):
    @abstractmethod
    def evaluate(self, dataset_processed: Dict[str, Dict]) -> Dict[str, Dict]:
        pass


class ISummaryGenerator(ABC):
    @abstractmethod
    def generate_summary(self, dataset_evaluated: Dict[str, Dict]) -> Dict:
        pass


# ==================================
#  Domain Implementations
# ==================================


class GlueTableProcessor(ITableProcessor):
    def __init__(self, glue_client):
        self.glue_client = glue_client

    def process_table(self, db_name, table_name):
        try:
            # Call AWS Glue API here
            self.glue_client.get_table(DatabaseName=db_name, Name=table_name)
            return {"status": "SUCCESS", "error": None}
        except Exception as e:
            return {"status": "FAILURE", "error": str(e)}


class TableProcessor(ITableProcessor):
    """Concrete implementation of a table processor."""

    def process_table(self, db_name: str, table_name: str) -> Dict[str, str]:
        try:
            # Example of actual Glue client logic
            return {"status": "SUCCESS", "error": None}
        except Exception as e:
            return {"status": "FAILURE", "error": str(e)}


class DatabaseProcessor(IDatabaseProcessor):
    """Processes multiple databases using a TableProcessor."""

    def __init__(self, table_processor: ITableProcessor):
        self.table_processor = table_processor

    def process_databases(self, entity_list: Dict[str, List[str]]) -> Dict[str, Dict]:
        dataset_processed = {}

        for db_name, tables in entity_list.items():
            print(f"\nProcessing database: {db_name}")

            db_result = {"result": None, "tables": {}}

            for table in tables:
                db_result["tables"][table] = self.table_processor.process_table(
                    db_name, table
                )

            dataset_processed[db_name] = db_result

        return dataset_processed


class ResultEvaluator(IResultEvaluator):
    """Evaluates overall database success/failure."""

    def evaluate(self, dataset_processed: Dict[str, Dict]) -> Dict[str, Dict]:
        for db_name, db_data in dataset_processed.items():
            table_statuses = [t["status"] for t in db_data["tables"].values()]
            db_data["result"] = (
                "SUCCESS"
                if all(status == "SUCCESS" for status in table_statuses)
                else "FAILURE"
            )
        return dataset_processed


class SummaryGenerator(ISummaryGenerator):
    """Generates global metrics."""

    def generate_summary(self, dataset_evaluated: Dict[str, Dict]) -> Dict:
        return {
            "databases_total": len(dataset_evaluated),
            "databases_success": sum(
                1 for db in dataset_evaluated.values() if db["result"] == "SUCCESS"
            ),
            "databases_failure": sum(
                1 for db in dataset_evaluated.values() if db["result"] == "FAILURE"
            ),
            "tables_total": sum(len(db["tables"]) for db in dataset_evaluated.values()),
            "tables_success": sum(
                1
                for db in dataset_evaluated.values()
                for t in db["tables"].values()
                if t["status"] == "SUCCESS"
            ),
            "tables_failure": sum(
                1
                for db in dataset_evaluated.values()
                for t in db["tables"].values()
                if t["status"] == "FAILURE"
            ),
        }


# ==================================
#  Application Layer — Pipeline Orchestration
# ==================================


class ProcessingPipeline:
    """
    Orchestrates database processing pipeline.
    Fully dependency-injected to respect DIP.
    """

    def __init__(
        self,
        db_processor: IDatabaseProcessor,
        evaluator: IResultEvaluator,
        summary_generator: ISummaryGenerator,
    ):
        self.db_processor = db_processor
        self.evaluator = evaluator
        self.summary_generator = summary_generator

    def run(self, entity_list: Dict[str, List[str]]) -> Dict:
        dataset_processed = self.db_processor.process_databases(entity_list)
        dataset_evaluated = self.evaluator.evaluate(dataset_processed)
        summary = self.summary_generator.generate_summary(dataset_evaluated)

        return {
            "processed": dataset_processed,
            "evaluated": dataset_evaluated,
            "summary": summary,
        }


# ==================================
#  Interface Layer — Main Application Entry
# ==================================


def main():
    # Define entities to process
    entity_list = {"ics_database_1": ["table1", "table2"], "ics_database_2": ["table1"]}

    print("Entity List:\n", json.dumps(entity_list, indent=4))

    # Dependency injection
    table_processor = TableProcessor()
    # table_processor = GlueTableProcessor(glue_client)
    db_processor = DatabaseProcessor(table_processor)
    evaluator = ResultEvaluator()
    summary_generator = SummaryGenerator()

    # Build pipeline (depending only on abstractions)
    pipeline = ProcessingPipeline(db_processor, evaluator, summary_generator)

    # Execute
    results = pipeline.run(entity_list)

    # Output results
    print("\nDataset Processed:\n", json.dumps(results["evaluated"], indent=4))
    print("\nGlobal Summary:\n", json.dumps(results["summary"], indent=4))


if __name__ == "__main__":
    main()
