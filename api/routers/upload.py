"""File upload endpoints."""

import os
import shutil
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from database.session import get_db
from database.models.user import User
from core.security import get_current_user
from repositories.file_repository import FileRepository
from services.prediction_service import PredictionService
from schemas.upload import UploadResponse
from configs.settings import settings
from utils.validators import validate_file
from utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/file", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    project_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a file for analysis."""
    # Validate file
    validate_file(file.filename, file.content_type, file.size)

    # Save file to disk
    file_path = os.path.join(settings.UPLOAD_DIR, f"{current_user.id}_{file.filename}")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Store in DB
    file_repo = FileRepository(db)
    db_file = file_repo.create(
        filename=file.filename,
        file_path=file_path,
        file_size_bytes=file.size,
        mime_type=file.content_type,
        project_id=project_id,
        uploaded_by=current_user.id,
    )
    db.commit()
    db.refresh(db_file)

    # Trigger background prediction (Celery) - we'll handle in predict service
    prediction_service = PredictionService(...)  # Not yet instantiated; we'll do later

    return UploadResponse(
        id=db_file.id,
        filename=db_file.filename,
        status=db_file.status,
        created_at=db_file.created_at,
    )