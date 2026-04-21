from __future__ import annotations

from datetime import datetime
from typing import Annotated, Optional, List
from pydantic import BaseModel, EmailStr, Field

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

from pydantic import BaseModel, EmailStr, constr

class UserCreate(UserBase):
    password: Annotated[str, Field(min_length=8, max_length=128)]
    role: str

class UserRead(UserBase):
    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class SubjectCreate(BaseModel):
    name: str

class SubjectRead(BaseModel):
    id: int
    name: str
    professor_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AnswerKeyCreate(BaseModel):
    subject_id: int
    content: str

class AnswerKeyRead(BaseModel):
    id: int
    subject_id: int
    filename: str
    content: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

class StudentCopyRead(BaseModel):
    id: int
    subject_id: int
    student_name: str
    student_email: Optional[EmailStr] = None
    filename: str
    status: str
    extracted_text: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True

class EvaluationRead(BaseModel):
    id: int
    score: float
    max_score: float
    feedback: Optional[str] = None
    report_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class EvaluationResponse(BaseModel):
    student_copy: StudentCopyRead
    evaluation: Optional[EvaluationRead]

class UploadResponse(BaseModel):
    success: bool
    message: str

class EvaluationTriggerRequest(BaseModel):
    subject_id: int
    max_score: float = 100.0
    weightage: Optional[dict] = None


class EvaluationUpdate(BaseModel):
    score: float
    feedback: Optional[str] = None


class StudentResultWithGrades(BaseModel):
    copy_id: int
    student_name: str
    student_email: Optional[str]
    roll_number: Optional[str]
    score: float
    max_score: float
    percentage: float
    feedback: Optional[str]
    status: str
    
    class Config:
        from_attributes = True
    weightage: Optional[dict] = None
    use_semantic_scoring: bool = True
