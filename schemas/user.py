from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    organization_id = Column(String(36), nullable=True)  # ForeignKey to Organization

    # Relationships
    projects = relationship("Project", back_populates="owner")
    uploads = relationship("UploadedFile", back_populates="uploader")
    predictions = relationship("Prediction", back_populates="user")
    reports = relationship("Report", back_populates="creator")
    api_keys = relationship("ApiKey", back_populates="user")