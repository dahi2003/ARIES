from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from ..dependencies import get_db, require_role
from .. import crud
from ..services.storage import save_upload
from ..services.security import validate_upload_filename, validate_file_content, scan_for_viruses
from ..services.gemini_service import extract_answer_key_with_gemini

router = APIRouter(prefix='/api/uploads', tags=['uploads'])

@router.post('/subject', status_code=status.HTTP_201_CREATED)
def create_subject(name: str = Form(...), current_user = Depends(require_role('professor', 'superadmin')), db: Session = Depends(get_db)):
    subject = crud.create_subject(db, professor_id=current_user.id, name=name)
    return {'id': subject.id, 'name': subject.name}

@router.post('/answer-key', status_code=status.HTTP_201_CREATED)
async def upload_answer_key(  # <-- Isko async banaya
    subject_id: int = Form(...),
    file: UploadFile = File(...),
    current_user = Depends(require_role('professor', 'superadmin')),
    db: Session = Depends(get_db),
):
    filename = file.filename or 'answer-key.pdf'
    validate_upload_filename(filename)
    
    # 1. File ko disk par save karo
    path = save_upload(file)
    validate_file_content(path)
    scan_for_viruses(path)
    
    # 2. Saved file ko bytes mein read karke Gemini ko bhejo
    try:
        with open(path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
            
        text = await extract_answer_key_with_gemini(pdf_bytes)
        
        if not text:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Gemini returned empty text for the answer key.')
            
    except Exception as e:
        
        print("====== ASLI ERROR YAHAN HAI ======")
        print(str(e))
        print("===================================")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Answer key processing failed: {str(e)}")
    # 3. Clean text database me save hoga
    answer_key = crud.create_answer_key(db, subject_id=subject_id, filename=filename, content=text)
    return {'id': answer_key.id, 'subject_id': subject_id, 'filename': answer_key.filename}


@router.post('/student-copies', status_code=status.HTTP_201_CREATED)
def upload_student_copies(
    subject_id: int = Form(...),
    student_name: str = Form(...),
    student_email: Optional[str] = Form(None),
    roll_number: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    current_user = Depends(require_role('professor', 'superadmin')),
    db: Session = Depends(get_db),
):
    saved = []
    for file in files:
        filename = file.filename or 'student-copy.pdf'
        validate_upload_filename(filename)
        
       
        path = save_upload(file)
        validate_file_content(path)
        scan_for_viruses(path)
        
       
        copy = crud.create_student_copy(
            db,
            subject_id=subject_id,
            student_name=student_name,
            student_email=student_email,
            filename=filename,
            roll_number=roll_number,
            extracted_text='', 
            file_path=str(path) 
        )
        saved.append({'copy_id': copy.id, 'filename': file.filename, 'status': copy.status})
        
    return {'uploaded': saved}


@router.get('/subjects')
def list_professor_subjects(
    current_user = Depends(require_role('professor', 'superadmin')),
    db: Session = Depends(get_db),
):
    subjects = crud.list_subjects_for_professor(db, current_user.id)
    return [
        {'id': subject.id, 'name': subject.name, 'created_at': subject.created_at.isoformat()}
        for subject in subjects
    ]


@router.get('/subject/{subject_id}/copies')
def list_subject_copies(
    subject_id: int,
    current_user = Depends(require_role('professor', 'superadmin')),
    db: Session = Depends(get_db),
):
    subject = crud.get_subject_by_id(db, subject_id)
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Subject not found')
    if subject.professor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Insufficient permissions')
        
    copies = crud.get_student_copies_by_subject(db, subject_id)
    return [
        {
            'id': copy.id,
            'subject_id': copy.subject_id,
            'student_name': copy.student_name,
            'student_email': copy.student_email,
            'roll_number': copy.roll_number,
            'filename': copy.filename,
            'status': copy.status,
            'uploaded_at': copy.uploaded_at.isoformat(),
        }
        for copy in copies
    ]