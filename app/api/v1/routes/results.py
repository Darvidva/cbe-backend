from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.core.deps import get_db, require_student, get_current_user
from app.db.models.result import Result
from app.db.models.subject import Subject
from app.db.models.user import User
from pydantic import BaseModel

router = APIRouter()

class ResultOut(BaseModel):
    id: int
    student_id: int
    student_name: str
    subject_id: int
    subject_name: str
    score: int
    total: int
    percentage: float
    grade: str | None
    status: str
    created_at: str

@router.get("/me", response_model=List[ResultOut], dependencies=[Depends(require_student)])
def get_my_results(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get all results for the current student"""
    results = db.query(Result).filter(Result.student_id == user.id).all()
    
    return [
        ResultOut(
            id=result.id,
            student_id=result.student_id,
            student_name=user.name,
            subject_id=result.subject_id,
            subject_name=db.query(Subject).filter(Subject.id == result.subject_id).first().name,
            score=result.score,
            total=result.total,
            percentage=result.percentage,
            grade=result.grade,
            status=result.status,
            created_at=result.created_at.isoformat()
        )
        for result in results
    ]

@router.get("/{result_id}", response_model=ResultOut, dependencies=[Depends(require_student)])
def get_result(result_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get a specific result by ID"""
    result = db.query(Result).filter(Result.id == result_id, Result.student_id == user.id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    subject = db.query(Subject).filter(Subject.id == result.subject_id).first()
    
    return ResultOut(
        id=result.id,
        student_id=result.student_id,
        student_name=user.name,
        subject_id=result.subject_id,
        subject_name=subject.name if subject else "Unknown Subject",
        score=result.score,
        total=result.total,
        percentage=result.percentage,
        grade=result.grade,
        status=result.status,
        created_at=result.created_at.isoformat()
    )

@router.get("/", response_model=List[ResultOut])
def get_all_results(db: Session = Depends(get_db)):
    """Get all results (admin only)"""
    results = db.query(Result).all()
    
    return [
        ResultOut(
            id=result.id,
            student_id=result.student_id,
            student_name=db.query(User).filter(User.id == result.student_id).first().name,
            subject_id=result.subject_id,
            subject_name=db.query(Subject).filter(Subject.id == result.subject_id).first().name,
            score=result.score,
            total=result.total,
            percentage=result.percentage,
            grade=result.grade,
            status=result.status,
            created_at=result.created_at.isoformat()
        )
        for result in results
    ]
