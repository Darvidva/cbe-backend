from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.deps import get_db, require_admin
from app.db.models.question import Question
from app.db.models.subject import Subject

router = APIRouter()

from enum import Enum
from typing import Literal

class OptionLetter(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"

class QuestionIn(BaseModel):
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: OptionLetter

class QuestionOut(BaseModel):
    id: int
    subject_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: OptionLetter
    
    class Config:
        from_attributes = True

# @router.post("/{subject_id}", response_model=QuestionOut, dependencies=[Depends(require_admin)])
# def add_question(subject_id: int, data: QuestionIn, db: Session = Depends(get_db)):
#     if not db.get(Subject, subject_id):
#         raise HTTPException(status_code=404, detail="Subject not found")
    
#     # Convert correct_option to string value
#     question_data = data.dict()
#     question_data['correct_option'] = question_data['correct_option'].value
    
#     q = Question(subject_id=subject_id, **question_data)
#     db.add(q)
#     db.commit()
#     db.refresh(q)
#     return q

@router.post("/{subject_id}", response_model=QuestionOut, dependencies=[Depends(require_admin)])
def add_question(subject_id: int, data: QuestionIn, db: Session = Depends(get_db)):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Count existing questions for this subject
    question_count = db.query(Question).filter(Question.subject_id == subject_id).count()
    if subject.totalQuestions is not None and question_count >= subject.totalQuestions:
        raise HTTPException(status_code=400, detail="Maximum number of questions reached for this subject")

    # Convert correct_option to string value
    question_data = data.dict()
    question_data['correct_option'] = question_data['correct_option'].value
    
    q = Question(subject_id=subject_id, **question_data)
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


@router.get("/{subject_id}", response_model=list[QuestionOut])
def list_questions(subject_id: int, db: Session = Depends(get_db)):
    return db.query(Question).filter(Question.subject_id == subject_id).all()

@router.put("/{question_id}", response_model=QuestionOut, dependencies=[Depends(require_admin)])
def update_question(question_id: int, data: QuestionIn, db: Session = Depends(get_db)):
    q = db.get(Question, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Convert correct_option to string value
    question_data = data.dict()
    if 'correct_option' in question_data:
        question_data['correct_option'] = question_data['correct_option'].value
        
    for key, value in question_data.items():
        setattr(q, key, value)
    
    db.commit()
    db.refresh(q)
    return q

@router.delete("/{question_id}", dependencies=[Depends(require_admin)])
def delete_question(question_id: int, db: Session = Depends(get_db)):
    q = db.get(Question, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.delete(q)
    db.commit()
    return {"message": "Question deleted successfully"}
