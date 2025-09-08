from pydantic import BaseModel
from datetime import datetime

class SubjectBase(BaseModel):
    name: str
    description: str
    duration: int
    totalQuestions: int
    passingScore: float

class SubjectIn(SubjectBase):
    pass

class SubjectOut(SubjectBase):
    id: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
