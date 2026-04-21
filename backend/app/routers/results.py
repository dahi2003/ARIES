from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..dependencies import get_db, get_current_user, require_role
from .. import crud
from ..schemas import EvaluationRead, StudentCopyRead

router = APIRouter(prefix='/api/results', tags=['results'])

@router.get('/subject/{subject_id}', response_model=List[EvaluationRead])
def results_for_subject(subject_id: int, current_user = Depends(require_role('professor', 'superadmin')), db: Session = Depends(get_db)):
    return crud.list_results_for_subject(db, subject_id)

@router.get('/copy/{copy_id}')
def get_copy_evaluation(copy_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    copy = crud.get_copy_by_id(db, copy_id)
    if not copy:
        raise HTTPException(status_code=404, detail='Student copy not found')
    if current_user.role == 'professor' and copy.subject.professor_id != current_user.id:
        raise HTTPException(status_code=403, detail='Forbidden')
    if current_user.role == 'student' and copy.student_email != current_user.email:
        raise HTTPException(status_code=403, detail='Forbidden')
    evaluation = crud.get_evaluation_by_copy(db, copy.id)
    return {
        'copy': copy,
        'evaluation': evaluation,
    }

@router.get('/evaluated')
def get_all_evaluated_copies(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns all evaluated copies - students search by name to find theirs"""
    if current_user.role != 'student':
        raise HTTPException(status_code=403, detail='Only students may access results')
    return crud.list_all_evaluated_copies(db)

@router.get('/student')
def get_my_results(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != 'student':
        raise HTTPException(status_code=403, detail='Only students may access their results')
    return crud.list_student_results(db, current_user.email)
