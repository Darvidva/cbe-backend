from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from app.core.deps import get_db, require_student, get_current_user
from app.db.models.question import Question
from app.db.models.result import Result
from app.db.models.subject import Subject
from app.db.models.user import User

router = APIRouter()

class StartExamResponse(BaseModel):
    subject_id: int
    questions: list[dict]
    time_remaining: int

class AnswerIn(BaseModel):
    question_id: int
    selected_option: str  # "A" | "B" | "C" | "D"

class SubmitIn(BaseModel):
    subject_id: int
    answers: List[AnswerIn]

class ResultOut(BaseModel):
    id: int
    score: int
    total: int
    percentage: float
    grade: str | None
    status: str

def grade_from_percentage(p: float) -> tuple[str, str]:
    if p >= 70: return ("A", "PASS")
    if p >= 60: return ("B", "PASS")
    if p >= 50: return ("C", "PASS")
    if p >= 45: return ("D", "PASS")
    if p >= 40: return ("E", "PASS")
    return ("F", "FAIL")

@router.post("/start/{subject_id}", response_model=StartExamResponse, dependencies=[Depends(require_student)])
def start_exam(subject_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Prevent retake if result already exists for this student and subject
    existing = db.query(Result).filter(Result.student_id == user.id, Result.subject_id == subject_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already completed this exam")
    # Get all questions for this subject
    questions = db.query(Question).filter(Question.subject_id == subject_id).all()
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this subject")
    
    # Get subject duration directly to avoid relationship/lazy loading issues
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Convert questions to dict without correct answers
    questions_data = [{
        "id": q.id,
        "question_text": q.question_text,
        "options": {
            "A": q.option_a,
            "B": q.option_b,
            "C": q.option_c,
            "D": q.option_d,
        }
    } for q in questions]

    return {
        "subject_id": subject_id,
        "questions": questions_data,
        "time_remaining": subject.duration * 60  # Convert minutes to seconds
    }

@router.post("/submit", response_model=ResultOut, dependencies=[Depends(require_student)])
def submit_exam(payload: SubmitIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Get questions from database and load all attributes
    questions = (
        db.query(Question)
        .filter(Question.subject_id == payload.subject_id)
        .all()
    )
    if not questions:
        raise HTTPException(status_code=404, detail="No questions for this subject")
    
    # Force evaluation of all attributes to get plain Python objects
    total = len(questions)
    score = 0

    for question in questions:
        # Find matching answer for this question
        for answer in payload.answers:
            if answer.question_id == question.id and answer.selected_option == question.correct_option:
                score += 1
                break
    
    percentage = (score / total * 100) if total else 0.0
    grade, status = grade_from_percentage(percentage)
    # store result
    res = Result(
        student_id=user.id,
        subject_id=payload.subject_id,
        score=score,
        total=total,
        percentage=percentage,
        grade=grade,
        status=status,
    )
    db.add(res)
    db.commit()
    db.refresh(res)  # Refresh to get the ID
    return ResultOut(id=res.id, score=score, total=total, percentage=percentage, grade=grade, status=status)
