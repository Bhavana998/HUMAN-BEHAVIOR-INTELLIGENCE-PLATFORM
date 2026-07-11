# database/models/project.py
from sqlalchemy import Column, String, Boolean
from .base import BaseModel

class Project(BaseModel):
    __tablename__ = "projects"
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    is_active = Column(Boolean, default=True)
    # No foreign keys, no relationships.