from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from . import models, schemas
from .auth import get_password_hash


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_count(db: Session) -> int:
    return db.query(models.User).count()


def create_user(db: Session, user_create: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user_create.password)
    user = models.User(
        email=user_create.email,
        full_name=user_create.full_name,
        role=user_create.role,
        hashed_password=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_subject_by_id(db: Session, subject_id: int) -> Optional[models.Subject]:
    return db.query(models.Subject).filter(models.Subject.id == subject_id).first()


def list_subjects_for_professor(db: Session, professor_id: int) -> List[models.Subject]:
    return db.query(models.Subject).filter(models.Subject.professor_id == professor_id).all()


def create_subject(db: Session, professor_id: int, name: str) -> models.Subject:
    subject = models.Subject(name=name, professor_id=professor_id)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def create_answer_key(db: Session, subject_id: int, filename: str, content: str) -> models.AnswerKey:
    answer_key = models.AnswerKey(subject_id=subject_id, filename=filename, content=content)
    db.add(answer_key)
    db.commit()
    db.refresh(answer_key)
    return answer_key


def create_student_copy(
    db: Session,
    subject_id: int,
    student_name: str,
    student_email: Optional[str],
    filename: str,
    roll_number: Optional[str] = None,
    extracted_text: Optional[str] = None,
    file_path: Optional[str] = None,
) -> models.StudentCopy:
    copy = models.StudentCopy(
        subject_id=subject_id,
        student_name=student_name,
        student_email=student_email,
        filename=filename,
        roll_number=roll_number,
        extracted_text=extracted_text,
        file_path=file_path,
    )
    db.add(copy)
    db.commit()
    db.refresh(copy)
    return copy


def get_student_copies_by_subject(db: Session, subject_id: int) -> List[models.StudentCopy]:
    return db.query(models.StudentCopy).filter(models.StudentCopy.subject_id == subject_id).all()


def list_student_results(db: Session, student_email: str) -> list[dict]:
    results = []
    rows = (
        db.query(models.StudentCopy, models.Evaluation)
        .outerjoin(models.Evaluation, models.Evaluation.copy_id == models.StudentCopy.id)
        .filter(models.StudentCopy.student_email == student_email)
        .all()
    )
    for copy, evaluation in rows:
        results.append({
            'copy_id': copy.id,
            'subject_id': copy.subject_id,
            'subject_name': copy.subject.name if copy.subject else None,
            'student_name': copy.student_name,
            'status': copy.status,
            'score': evaluation.score if evaluation else None,
            'max_score': evaluation.max_score if evaluation else None,
            'feedback': evaluation.feedback if evaluation else None,
            'report_path': evaluation.report_path if evaluation else None,
            'uploaded_at': copy.uploaded_at,
        })
    return results


def get_copy_by_id(db: Session, copy_id: int) -> Optional[models.StudentCopy]:
    return db.query(models.StudentCopy).filter(models.StudentCopy.id == copy_id).first()


def update_copy_status(db: Session, copy: models.StudentCopy, status: str) -> models.StudentCopy:
    copy.status = status
    db.commit()
    db.refresh(copy)
    return copy


def create_evaluation(
    db: Session,
    copy_id: int,
    score: float,
    max_score: float,
    feedback: str,
    report_path: str,
) -> models.Evaluation:
    evaluation = models.Evaluation(
        copy_id=copy_id,
        score=score,
        max_score=max_score,
        feedback=feedback,
        report_path=report_path,
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation


def get_evaluation_by_copy(db: Session, copy_id: int) -> Optional[models.Evaluation]:
    return db.query(models.Evaluation).filter(models.Evaluation.copy_id == copy_id).first()


def list_all_evaluated_copies(db: Session) -> list[dict]:
    """List all evaluated student copies for students to search"""
    results = []
    rows = (
        db.query(models.StudentCopy, models.Evaluation)
        .join(models.Evaluation, models.Evaluation.copy_id == models.StudentCopy.id)
        .all()
    )
    for copy, evaluation in rows:
        results.append({
            'copy_id': copy.id,
            'subject_id': copy.subject_id,
            'subject_name': copy.subject.name if copy.subject else None,
            'student_name': copy.student_name,
            'student_email': copy.student_email,
            'status': copy.status,
            'score': evaluation.score,
            'max_score': evaluation.max_score,
            'feedback': evaluation.feedback,
            'report_path': evaluation.report_path,
            'uploaded_at': copy.uploaded_at,
        })
    return results


def list_results_for_subject(db: Session, subject_id: int) -> List[models.Evaluation]:
    return (
        db.query(models.Evaluation)
        .join(models.StudentCopy, models.Evaluation.copy_id == models.StudentCopy.id)
        .filter(models.StudentCopy.subject_id == subject_id)
        .all()
    )
