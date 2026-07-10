"""Service for making predictions and managing prediction records."""

import asyncio
from typing import List, Dict, Any, Optional
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from repositories.prediction_repository import PredictionRepository
from repositories.file_repository import FileRepository
from database.models.user import User
from schemas.prediction import PredictionResponse
from inference.predictor import Predictor
from inference.explainer import Explainer
from tasks.prediction_tasks import run_prediction_async
from utils.logger import get_logger
from core.exceptions import ValidationError

logger = get_logger(__name__)


class PredictionService:
    def __init__(
        self,
        pred_repo: PredictionRepository,
        file_repo: FileRepository,
        user: User,
    ):
        self.pred_repo = pred_repo
        self.file_repo = file_repo
        self.user = user
        self.predictor = Predictor()
        self.explainer = Explainer()

    async def predict_single(
        self,
        text: str,
        tasks: List[str],
        project_id: Optional[str] = None,
        file_id: Optional[str] = None,
    ) -> PredictionResponse:
        """Run predictions synchronously for a single text."""
        # Validate tasks
        valid_tasks = set(self.predictor.available_tasks())
        invalid = set(tasks) - valid_tasks
        if invalid:
            raise ValidationError(f"Invalid tasks: {invalid}")

        # Perform prediction
        results = await self.predictor.predict(text, tasks)

        # Compute explanations if requested (we'll always compute for now)
        explanations = await self.explainer.explain(text, tasks, results)

        # Save to DB
        pred_record = self.pred_repo.create(
            input_text=text,
            task_type=",".join(tasks),
            result=results,
            confidence={k: v.get("confidence") for k, v in results.items()},
            explanation=explanations,
            user_id=self.user.id,
            uploaded_file_id=file_id,
        )
        self.pred_repo.db.commit()
        self.pred_repo.db.refresh(pred_record)

        # Also store individual behavior scores if needed
        # ...

        return PredictionResponse(
            id=pred_record.id,
            input_text=text,
            task_type=pred_record.task_type,
            result=results,
            confidence=pred_record.confidence,
            explanation=explanations,
            status="success",
            created_at=pred_record.created_at,
        )

    async def predict_batch_async(
        self,
        texts: List[str],
        tasks: List[str],
        project_id: Optional[str] = None,
    ) -> str:
        """Submit a batch prediction job to Celery."""
        # Generate a job ID
        job_id = self.pred_repo.create_batch_job(texts, tasks, self.user.id, project_id)
        # Trigger Celery task
        run_prediction_async.delay(job_id, texts, tasks, self.user.id, project_id)
        return job_id