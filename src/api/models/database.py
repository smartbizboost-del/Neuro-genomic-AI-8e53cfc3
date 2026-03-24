"""
SQLAlchemy database models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

Base = declarative_base()

class FileUpload(Base):
    __tablename__ = "file_uploads"
    
    id = Column(String(36), primary_key=True)
    filename = Column(String(255))
    s3_key = Column(String(500))
    size = Column(Integer)
    gestational_weeks = Column(Integer, nullable=True)
    patient_id = Column(String(100), nullable=True)
    status = Column(String(50), default="uploaded")
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationship
    analysis = relationship("AnalysisResult", back_populates="file", uselist=False)

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(String(36), ForeignKey("file_uploads.id"))
    features = Column(JSON)
    risk_assessment = Column(JSON)
    developmental_index = Column(Float)
    interpretation = Column(JSON)
    confidence_intervals = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationship
    file = relationship("FileUpload", back_populates="analysis")