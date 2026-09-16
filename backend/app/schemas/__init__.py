"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base user schema."""
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    role: str = Field(default="STUDENT")
    phone: Optional[str] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8)

    @validator("password")
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class UserResponse(UserBase):
    """User response schema."""
    id: int
    student_id: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdmissionBase(BaseModel):
    """Base admission schema."""
    course: str
    branch: str
    semester: int
    admission_year: int


class AdmissionCreate(AdmissionBase):
    """Admission creation schema."""
    user_id: int
    admission_date: datetime


class AdmissionResponse(AdmissionBase):
    """Admission response schema."""
    id: int
    student_id: str
    status: str
    gpa: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    """Base document schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: str
    branch: Optional[str] = None
    semester: Optional[int] = None
    role_access: List[str] = []


class DocumentResponse(DocumentBase):
    """Document response schema."""
    id: int
    file_path: str
    file_size: int
    uploaded_by: Optional[int]
    is_indexed: bool
    indexing_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DeadlineBase(BaseModel):
    """Base deadline schema."""
    title: str
    description: Optional[str] = None
    type: str
    due_date: datetime


class DeadlineResponse(DeadlineBase):
    """Deadline response schema."""
    id: int
    status: str
    is_submitted: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProblemReportCreate(BaseModel):
    """Problem report creation schema."""
    type: str
    title: str
    description: str
    priority: str = "MEDIUM"


class ProblemReportResponse(ProblemReportCreate):
    """Problem report response schema."""
    id: int
    uuid: str
    status: str
    resolution_steps: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QueryCreate(BaseModel):
    """Query creation schema."""
    query: str = Field(..., min_length=5)


class QueryResponse(QueryCreate):
    """Query response schema."""
    id: int
    answer: Optional[str]
    source_documents: List[int]
    created_at: datetime
    answered_at: Optional[datetime]

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
