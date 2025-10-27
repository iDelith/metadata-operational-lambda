from app.src.application.workflows.update_database_location_pipeline import (
    UpdateDatabaseLocationPipeline,
)
from app.src.application.workflows.update_description_pipeline import (
    UpdateDescriptionPipeline,
)
from app.src.infrastructure.clients.aws_client_provider import AWSClientProvider
from app.src.infrastructure.clients.mock_client_provider import MockClientProvider


class PipelineFactory:
    def __init__(self, use_mock=False):
        self.client_provider = MockClientProvider() if use_mock else AWSClientProvider()
        self.operations = {
            "update_description": UpdateDescriptionPipeline,
            "update_database_location": UpdateDatabaseLocationPipeline,
        }

    def create_pipeline(self, operation_type):
        operation_cls = self.operations.get(operation_type)
        if not operation_cls:
            raise ValueError(f"Unsupported operation: {operation_type}")
        return operation_cls(client_provider=self.client_provider)
