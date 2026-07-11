from sqlalchemy import Column, String, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Prediction(BaseModel):
    __tablename__ = "predictions"

    input_text = Column(Text, nullable=False)
    task_type = Column(String(100), nullable=False)
    model_version = Column(String(100), nullable=True)
    result = Column(JSON, nullable=True)
    confidence = Column(JSON, nullable=True)
    explanation = Column(JSON, nullable=True)
    status = Column(String(50), default="pending")
    error_message = Column(String(500), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    uploaded_file_id = Column(String(36), ForeignKey("uploaded_files.id"), nullable=True)

    user = relationship("User", back_populates="predictions")
    uploaded_file = relationship("UploadedFile", back_populates="predictions")
    scores = relationship("BehaviorScore", back_populates="prediction")