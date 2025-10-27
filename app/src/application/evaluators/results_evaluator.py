class ResultEvaluator:
    def evaluate_results(self, dataset_processed):
        for db_name, db_data in dataset_processed.items():
            table_statuses = [t["status"] for t in db_data["tables"].values()]
            db_data["result"] = (
                "SUCCESS"
                if all(status == "SUCCESS" for status in table_statuses)
                else "FAILURE"
            )
