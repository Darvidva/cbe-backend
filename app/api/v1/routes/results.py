from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.subject import Subject
from app.core.deps import get_db, require_admin, get_current_user
from app.db.models.result import Result
from app.db.models.user import User

router = APIRouter()

class ResultRow(BaseModel):
    id: int
    student_id: int
    subject_id: int
    student_name: str
    subject_name: str
    score: int
    total: int
    percentage: float
    grade: str | None
    status: str

    class Config:
        from_attributes = True

@router.get("/", response_model=list[ResultRow], dependencies=[Depends(require_admin)])
def list_all_results(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Result.id,
            Result.student_id,
            Result.subject_id,
            User.name.label("student_name"),
            Subject.name.label("subject_name"),
            Result.score,
            Result.total,
            Result.percentage,
            Result.grade,
            Result.status,
        )
        .join(User, User.id == Result.student_id)
        .join(Subject, Subject.id == Result.subject_id)
        .order_by(Result.id.desc())
        .all()
    )
    # rows are tuples; convert to dicts matching ResultRow
    result = [
        {
            "id": r[0],
            "student_id": r[1],
            "subject_id": r[2],
            "student_name": r[3],
            "subject_name": r[4],
            "score": r[5],
            "total": r[6],
            "percentage": r[7],
            "grade": r[8],
            "status": r[9],
        }
        for r in rows
    ]
    return result

@router.get("/me", response_model=list[ResultRow])
def my_results(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(
            Result.id,
            Result.student_id,
            Result.subject_id,
            User.name.label("student_name"),
            Subject.name.label("subject_name"),
            Result.score,
            Result.total,
            Result.percentage,
            Result.grade,
            Result.status,
        )
        .join(User, User.id == Result.student_id)
        .join(Subject, Subject.id == Result.subject_id)
        .filter(Result.student_id == user.id)
        .order_by(Result.id.desc())
        .all()
    )
    return [
        {
            "id": r[0],
            "student_id": r[1],
            "subject_id": r[2],
            "student_name": r[3],
            "subject_name": r[4],
            "score": r[5],
            "total": r[6],
            "percentage": r[7],
            "grade": r[8],
            "status": r[9],
        }
        for r in rows
    ]
