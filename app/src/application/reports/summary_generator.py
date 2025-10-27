class SummaryGenerator:
    def generate_summary(self, dataset_processed):
        databases_total = len(dataset_processed)
        databases_success = sum(
            1 for db in dataset_processed.values() if db["result"] == "SUCCESS"
        )
        databases_failure = sum(
            1 for db in dataset_processed.values() if db["result"] == "FAILURE"
        )

        tables_total = sum(len(db["tables"]) for db in dataset_processed.values())
        tables_success = sum(
            1
            for db in dataset_processed.values()
            for table in db["tables"].values()
            if table["status"] == "SUCCESS"
        )
        tables_failure = tables_total - tables_success

        return (
            f"Databases - Total: {databases_total}\n"
            f"Databases - Success: {databases_success}\n"
            f"Databases - Failure: {databases_failure}\n\n"
            f"Tables - Total: {tables_total}\n"
            f"Tables - Success: {tables_success}\n"
            f"Tables - Failure: {tables_failure}"
        )
