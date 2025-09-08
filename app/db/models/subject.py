from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float
from app.db.session import Base

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    totalQuestions = Column(Integer, nullable=False)
    passingScore = Column(Float, nullable=False)  # percentage
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
