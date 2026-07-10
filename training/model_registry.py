"""MLflow model registry."""

import mlflow
from mlflow.tracking import MlflowClient
from configs.settings import settings

class ModelRegistryService:
    def __init__(self):
        self.client = MlflowClient(tracking_uri=settings.MLFLOW_TRACKING_URI)

    def register_model(self, run_id: str, model_name: str, version: str = "1"):
        """Register a model in MLflow Model Registry."""
        model_uri = f"runs:/{run_id}/model"
        model_details = mlflow.register_model(model_uri, model_name)
        return model_details

    def get_latest_version(self, model_name: str, stage: str = "Production"):
        """Get the latest model version in a stage."""
        versions = self.client.get_latest_versions(model_name, stages=[stage])
        if versions:
            return versions[0]
        return None