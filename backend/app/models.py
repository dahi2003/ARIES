from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default='student')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    subjects: Mapped[List[Subject]] = relationship('Subject', back_populates='professor')

class Subject(Base):
    __tablename__ = 'subjects'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    professor_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    professor: Mapped[User] = relationship('User', back_populates='subjects')
    answer_keys: Mapped[List[AnswerKey]] = relationship('AnswerKey', back_populates='subject')
    student_copies: Mapped[List[StudentCopy]] = relationship('StudentCopy', back_populates='subject')

class AnswerKey(Base):
    __tablename__ = 'answer_keys'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey('subjects.id'), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    subject: Mapped[Subject] = relationship('Subject', back_populates='answer_keys')

class StudentCopy(Base):
    __tablename__ = 'student_copies'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey('subjects.id'), nullable=False)
    student_name: Mapped[str] = mapped_column(String(255), nullable=False)
    student_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    roll_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='pending')
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    subject: Mapped[Subject] = relationship('Subject', back_populates='student_copies')
    evaluation: Mapped[Optional[Evaluation]] = relationship('Evaluation', back_populates='copy', uselist=False)

class Evaluation(Base):
    __tablename__ = 'evaluations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    copy_id: Mapped[int] = mapped_column(Integer, ForeignKey('student_copies.id'), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    max_score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    report_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    copy: Mapped[StudentCopy] = relationship('StudentCopy', back_populates='evaluation')
