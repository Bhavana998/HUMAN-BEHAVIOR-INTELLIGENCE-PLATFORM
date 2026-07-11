from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class ApiKey(BaseModel):
    __tablename__ = "api_keys"

    key_hash = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="api_keys")