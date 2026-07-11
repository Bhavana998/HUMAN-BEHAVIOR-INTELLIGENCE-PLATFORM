from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class UploadedFile(BaseModel):
    __tablename__ = "uploaded_files"

    filename = Column(String(255), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size_bytes = Column(Integer)
    mime_type = Column(String(100))
    status = Column(String(50), default="pending")
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    uploaded_by = Column(String(36), ForeignKey("users.id"), nullable=False)

    project = relationship("Project", back_populates="files")
    uploader = relationship("User", back_populates="uploads")
    predictions = relationship("Prediction", back_populates="uploaded_file")