from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class BehaviorScore(BaseModel):
    __tablename__ = "behavior_scores"

    prediction_id = Column(String(36), ForeignKey("predictions.id"), nullable=False)
    score_type = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    confidence = Column(Float, nullable=True)
    extra_metadata = Column(String(500), nullable=True)  # renamed from metadata

    prediction = relationship("Prediction", back_populates="scores")