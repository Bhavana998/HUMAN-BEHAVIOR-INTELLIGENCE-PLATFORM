# utils/validators.py
"""Validation utilities for file uploads and input data."""

import os
from fastapi import HTTPException, UploadFile
from configs.settings import settings


def validate_file(filename: str, content_type: str, file_size: int) -> None:
    """
    Validate an uploaded file.
    Raises HTTPException if validation fails.
    """
    # Check file size
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB} MB"
        )

    # Check allowed extensions (optional)
    allowed_extensions = {".txt", ".csv", ".json", ".xlsx", ".pdf", ".docx"}
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=415,
            detail=f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
        )

    # Check MIME type (optional)
    allowed_mime = [
        "text/plain", "text/csv", "application/json",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    if content_type not in allowed_mime:
        raise HTTPException(
            status_code=415,
            detail=f"MIME type not allowed. Allowed: {', '.join(allowed_mime)}"
        )