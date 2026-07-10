from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class PredictionRequest(BaseModel):
    text: str
    tasks: List[str]  # e.g., ["sentiment", "emotion"]
    project_id: Optional[str] = None
    file_id: Optional[str] = None


class BatchPredictionRequest(BaseModel):
    texts: List[str]
    tasks: List[str]
    project_id: Optional[str] = None


class PredictionResponse(BaseModel):
    id: str
    input_text: str
    task_type: str
    result: Dict[str, Any]
    confidence: Optional[Dict[str, float]]
    explanation: Optional[Dict[str, Any]]
    status: str
    created_at: datetime