"""API dependencies."""
from typing import Optional
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from database.session import get_db
from core.security import get_current_user
from database.models.user import User
from services.prediction_service import PredictionService
from services.training_service import TrainingService
from services.report_service import ReportService
from services.model_registry_service import ModelRegistryService
from repositories import (
    UserRepository, ProjectRepository, FileRepository,
    PredictionRepository, ReportRepository, AuditRepository
)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_project_repository(db: Session = Depends(get_db)) -> ProjectRepository:
    return ProjectRepository(db)


def get_file_repository(db: Session = Depends(get_db)) -> FileRepository:
    return FileRepository(db)


def get_prediction_repository(db: Session = Depends(get_db)) -> PredictionRepository:
    return PredictionRepository(db)


def get_report_repository(db: Session = Depends(get_db)) -> ReportRepository:
    return ReportRepository(db)


def get_audit_repository(db: Session = Depends(get_db)) -> AuditRepository:
    return AuditRepository(db)


def get_prediction_service(
    pred_repo: PredictionRepository = Depends(get_prediction_repository),
    file_repo: FileRepository = Depends(get_file_repository),
    user: User = Depends(get_current_user),
) -> PredictionService:
    return PredictionService(pred_repo, file_repo, user)


def get_training_service() -> TrainingService:
    return TrainingService()


def get_report_service(
    report_repo: ReportRepository = Depends(get_report_repository),
    pred_repo: PredictionRepository = Depends(get_prediction_repository),
    user: User = Depends(get_current_user),
) -> ReportService:
    return ReportService(report_repo, pred_repo, user)


def get_model_registry_service() -> ModelRegistryService:
    return ModelRegistryService()