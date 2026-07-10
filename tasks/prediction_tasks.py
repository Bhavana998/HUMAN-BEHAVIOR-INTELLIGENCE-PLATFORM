"""Celery tasks for predictions."""

from celery import Task
from tasks.celery_app import celery_app
from inference.predictor import Predictor
from repositories.prediction_repository import PredictionRepository
from database.session import SessionLocal
from utils.logger import get_logger

logger = get_logger(__name__)


class PredictionTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Prediction task failed: {exc}")


@celery_app.task(base=PredictionTask, bind=True)
def run_prediction_async(self, job_id: str, texts: list, tasks: list, user_id: str, project_id: str):
    """Run batch prediction asynchronously."""
    db = SessionLocal()
    try:
        predictor = Predictor()
        pred_repo = PredictionRepository(db)
        results = []
        for text in texts:
            result = predictor.predict(text, tasks)
            # Store each prediction
            pred_record = pred_repo.create(
                input_text=text,
                task_type=",".join(tasks),
                result=result,
                user_id=user_id,
                project_id=project_id,  # need to add project_id to model
            )
            db.commit()
            results.append({"id": pred_record.id, "result": result})
        # Update job status to completed
        # ...
        logger.info(f"Batch prediction job {job_id} completed.")
    except Exception as e:
        logger.exception(f"Batch prediction job {job_id} failed: {e}")
        raise
    finally:
        db.close()