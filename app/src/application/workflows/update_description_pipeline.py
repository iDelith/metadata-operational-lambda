from app.src.application.workflows.base_pipeline import BasePipeline
from app.src.infrastructure.processors.glue_table_processor import GlueTableProcessor
from app.src.infrastructure.processors.local_table_processor import LocalTableProcessor


class UpdateDescriptionPipeline(BasePipeline):
    def __init__(self, client_provider):
        super().__init__()
        self.client_provider = client_provider
        glue_client = client_provider.get_glue_client()

        # Choose processor implementation
        if client_provider.is_mock:
            self.table_processor = LocalTableProcessor()
        else:
            self.table_processor = GlueTableProcessor(glue_client)

    def run(self, entity_list):
        dataset_processed = {}

        for db_name, tables in entity_list.items():
            print(f"\nProcessing database: {db_name}")
            dataset_processed[db_name] = {"result": None, "tables": {}}

            for table in tables:
                try:
                    result = self.table_processor.update_description(db_name, table)
                    dataset_processed[db_name]["tables"][table] = {
                        "status": "SUCCESS",
                        "details": result,
                        "error": None,
                    }
                except Exception as e:
                    dataset_processed[db_name]["tables"][table] = {
                        "status": "FAILURE",
                        "details": None,
                        "error": str(e),
                    }

        return self.finalize(dataset_processed)
