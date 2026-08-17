"""
Project Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    department: str = Field(..., min_length=2, max_length=100)
    academic_session: str = Field(..., min_length=4, max_length=50) # e.g. "2025/2026"
    supervisor_id: Optional[int] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    department: Optional[str] = None
    academic_session: Optional[str] = None
    supervisor_id: Optional[int] = None
    status: Optional[str] = None

class SupervisorSimple(BaseModel):
    id: int
    staff_id: Optional[str] = None
    full_name: str
    email: str

    model_config = ConfigDict(from_attributes=True)

class StudentSimple(BaseModel):
    id: int
    full_name: str
    email: str
    matric_number: Optional[str] = None
    department: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class SubmissionBrief(BaseModel):
    id: int
    version: int
    original_filename: str
    file_type: str
    file_size: int
    submission_status: str
    submitted_at: datetime
    similarity_score: Optional[float] = None
    plagiarism_result: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ProjectOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    department: str
    academic_session: str
    student_id: int
    supervisor_id: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime
    student: Optional[StudentSimple] = None
    supervisor_info: Optional[SupervisorSimple] = None
    submissions_count: int = 0
    latest_similarity_score: Optional[float] = None
    latest_submission_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class ProjectDetailOut(ProjectOut):
    submissions: List[SubmissionBrief] = []
    feedbacks_count: int = 0
