from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import BaseModel

class Organization(BaseModel):
    __tablename__ = "organizations"

    name = Column(String(255), nullable=False)
    plan = Column(String(50), default="free")
    settings = Column(String(1000), nullable=True)

    users = relationship("User", back_populates="organization")
    projects = relationship("Project", back_populates="organization")