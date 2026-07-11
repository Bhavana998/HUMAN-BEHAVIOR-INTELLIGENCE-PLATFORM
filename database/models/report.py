from sqlalchemy import Column, String, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Report(BaseModel):
    __tablename__ = "reports"

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    insights = Column(JSON, nullable=True)
    risk_analysis = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    generated_from = Column(String(36), ForeignKey("predictions.id"), nullable=True)

    project = relationship("Project", back_populates="reports")
    creator = relationship("User", back_populates="reports")
