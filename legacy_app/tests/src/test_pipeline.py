import pytest

# Import your actual modules here, e.g.:
# from pipeline_module import (
#     ITableProcessor, IDatabaseProcessor, IResultEvaluator, ISummaryGenerator,
#     ProcessingPipeline
# )


# For demonstration purposes, simplified interfaces and pipeline:
class ITableProcessor:
    def process_table(self, db_name: str, table_name: str): ...
class IDatabaseProcessor:
    def process_databases(self, entity_list): ...
class IResultEvaluator:
    def evaluate(self, dataset_processed): ...
class ISummaryGenerator:
    def generate_summary(self, dataset_evaluated): ...


class ProcessingPipeline:
    def __init__(self, db_processor, evaluator, summary_generator):
        self.db_processor = db_processor
        self.evaluator = evaluator
        self.summary_generator = summary_generator

    def run(self, entity_list):
        dataset_processed = self.db_processor.process_databases(entity_list)
        dataset_evaluated = self.evaluator.evaluate(dataset_processed)
        summary = self.summary_generator.generate_summary(dataset_evaluated)
        return {
            "processed": dataset_processed,
            "evaluated": dataset_evaluated,
            "summary": summary,
        }


# ------------------------
# Mock implementations
# ------------------------


class MockTableProcessor(ITableProcessor):
    def __init__(self, fail_on=None):
        self.fail_on = fail_on or []

    def process_table(self, db_name, table_name):
        if table_name in self.fail_on:
            return {"status": "FAILURE", "error": f"Table {table_name} failed"}
        return {"status": "SUCCESS", "error": None}


class MockDatabaseProcessor(IDatabaseProcessor):
    def __init__(self, table_processor):
        self.table_processor = table_processor

    def process_databases(self, entity_list):
        result = {}
        for db, tables in entity_list.items():
            result[db] = {
                "result": None,
                "tables": {
                    t: self.table_processor.process_table(db, t) for t in tables
                },
            }
        return result


class MockResultEvaluator(IResultEvaluator):
    def evaluate(self, dataset_processed):
        for db, data in dataset_processed.items():
            statuses = [t["status"] for t in data["tables"].values()]
            data["result"] = (
                "SUCCESS" if all(s == "SUCCESS" for s in statuses) else "FAILURE"
            )
        return dataset_processed


class MockSummaryGenerator(ISummaryGenerator):
    def generate_summary(self, dataset_evaluated):
        return {
            "databases_total": len(dataset_evaluated),
            "databases_success": sum(
                1 for d in dataset_evaluated.values() if d["result"] == "SUCCESS"
            ),
            "databases_failure": sum(
                1 for d in dataset_evaluated.values() if d["result"] == "FAILURE"
            ),
        }


# ------------------------
# Fixtures
# ------------------------


@pytest.fixture
def table_proc_success():
    return MockTableProcessor()


@pytest.fixture
def table_proc_failure():
    return MockTableProcessor(fail_on=["table2"])


@pytest.fixture
def evaluator():
    return MockResultEvaluator()


@pytest.fixture
def summary():
    return MockSummaryGenerator()


# ------------------------
# Tests
# ------------------------


def test_all_success(table_proc_success, evaluator, summary):
    db_proc = MockDatabaseProcessor(table_proc_success)
    pipeline = ProcessingPipeline(db_proc, evaluator, summary)

    entity_list = {"db1": ["table1"], "db2": ["tableA", "tableB"]}
    result = pipeline.run(entity_list)

    assert result["summary"]["databases_success"] == 2
    assert result["summary"]["databases_failure"] == 0


def test_partial_failure(table_proc_failure, evaluator, summary):
    db_proc = MockDatabaseProcessor(table_proc_failure)
    pipeline = ProcessingPipeline(db_proc, evaluator, summary)

    entity_list = {"db1": ["table1", "table2"], "db2": ["table3"]}
    result = pipeline.run(entity_list)

    assert result["summary"]["databases_total"] == 2
    assert result["summary"]["databases_success"] == 1
    assert result["summary"]["databases_failure"] == 1

    assert result["evaluated"]["db1"]["result"] == "FAILURE"
    assert result["evaluated"]["db2"]["result"] == "SUCCESS"


def test_empty_input(table_proc_success, evaluator, summary):
    db_proc = MockDatabaseProcessor(table_proc_success)
    pipeline = ProcessingPipeline(db_proc, evaluator, summary)

    result = pipeline.run({})
    assert result["summary"]["databases_total"] == 0
    assert result["summary"]["databases_success"] == 0
    assert result["summary"]["databases_failure"] == 0


def test_injection_flexibility(table_proc_success, evaluator, summary):
    """Ensures the pipeline can accept any class that implements the expected methods"""
    db_proc = MockDatabaseProcessor(table_proc_success)
    pipeline = ProcessingPipeline(db_proc, evaluator, summary)

    assert hasattr(pipeline.db_processor, "process_databases")
    assert hasattr(pipeline.evaluator, "evaluate")
    assert hasattr(pipeline.summary_generator, "generate_summary")
