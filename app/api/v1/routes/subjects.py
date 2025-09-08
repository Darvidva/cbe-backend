from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import require_admin
from app.db.models.subject import Subject
from app.api.v1.schemas.subject import SubjectIn, SubjectOut

router = APIRouter(prefix="")

@router.get("/", response_model=List[SubjectOut])
async def get_subjects(db: Session = Depends(get_db)):
    subjects = db.query(Subject).all()
    return subjects

@router.get("/{subject_id}", response_model=SubjectOut)
async def get_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.post("/", response_model=SubjectOut, dependencies=[Depends(require_admin)])
async def create_subject(data: SubjectIn, db: Session = Depends(get_db)):
    exists = db.query(Subject).filter(Subject.name == data.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Subject already exists")
    s = Subject(
        name=data.name,
        description=data.description,
        duration=data.duration,
        totalQuestions=data.totalQuestions,
        passingScore=data.passingScore
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

@router.put("/{subject_id}", response_model=SubjectOut, dependencies=[Depends(require_admin)])
async def update_subject(subject_id: int, data: SubjectIn, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    name_exists = db.query(Subject).filter(Subject.name == data.name, Subject.id != subject_id).first()
    if name_exists:
        raise HTTPException(status_code=400, detail="Subject with this name already exists")
    
    for key, value in data.model_dump().items():
        setattr(subject, key, value)
    
    db.commit()
    db.refresh(subject)
    return subject

@router.delete("/{subject_id}", dependencies=[Depends(require_admin)])
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    db.delete(subject)
    db.commit()
    return {"message": "Subject deleted successfully"}
