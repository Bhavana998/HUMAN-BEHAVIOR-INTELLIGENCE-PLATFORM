from pydantic import BaseModel
from datetime import datetime


class UploadResponse(BaseModel):
    id: str
    filename: str
    status: str
    created_at: datetime