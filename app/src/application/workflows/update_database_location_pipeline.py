from app.src.application.workflows.base_pipeline import BasePipeline


class UpdateDatabaseLocationPipeline(BasePipeline):
    def __init__(self, client_provider):
        super().__init__()
        self.client_provider = client_provider

    def run(self, entity_list):
        print("Running UpdateDatabaseLocationPipeline (not yet implemented)")
        dataset_processed = {
            db: {
                "result": "PENDING",
                "tables": {t: {"status": "PENDING"} for t in tbls},
            }
            for db, tbls in entity_list.items()
        }
        return self.finalize(dataset_processed)
