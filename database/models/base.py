import uuid
from sqlalchemy import Column, DateTime, String, func
from database.base import Base

class BaseModel(Base):
    __abstract__ = True
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)