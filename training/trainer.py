"""Model training orchestration."""

import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
import optuna
import joblib

from configs.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class Trainer:
    def __init__(self, model_type: str = "random_forest"):
        self.model_type = model_type
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        mlflow.set_experiment(settings.MLFLOW_EXPERIMENT_NAME)

    def train(self, X, y, hyperparams=None):
        """Train a model."""
        with mlflow.start_run() as run:
            # Log params
            mlflow.log_params(hyperparams or {})
            # Train model
            model = RandomForestClassifier(**hyperparams) if hyperparams else RandomForestClassifier()
            model.fit(X, y)
            # Evaluate
            preds = model.predict(X)
            acc = accuracy_score(y, preds)
            f1 = f1_score(y, preds, average="weighted")
            mlflow.log_metric("train_accuracy", acc)
            mlflow.log_metric("train_f1", f1)
            # Save model
            model_path = f"{settings.MODEL_STORAGE_PATH}/model_{run.info.run_id}.pkl"
            joblib.dump(model, model_path)
            mlflow.log_artifact(model_path)
            logger.info(f"Model trained and saved to {model_path}")
            return model

    def hyperparameter_tuning(self, X, y, n_trials=50):
        """Optuna hyperparameter optimization."""
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 300),
                "max_depth": trial.suggest_int("max_depth", 5, 30),
                "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
            }
            model = RandomForestClassifier(**params)
            # Cross-validation score
            from sklearn.model_selection import cross_val_score
            scores = cross_val_score(model, X, y, cv=3, scoring="f1_weighted")
            return scores.mean()

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials)
        best_params = study.best_params
        logger.info(f"Best hyperparameters: {best_params}")
        return best_params

    def cross_validate(self, X, y, params, cv=5):
        """Perform cross-validation."""
        from sklearn.model_selection import cross_val_score
        model = RandomForestClassifier(**params)
        scores = cross_val_score(model, X, y, cv=cv, scoring="f1_weighted")
        logger.info(f"Cross-validation scores: {scores}")
        return scores