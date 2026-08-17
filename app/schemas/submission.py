"""
Submission Pydantic schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class SubmissionOut(BaseModel):
    id: int
    project_id: int
    version: int
    original_filename: str
    stored_filename: str
    file_type: str
    file_size: int
    submitted_by: int
    submission_status: str
    submitted_at: datetime
    similarity_score: Optional[float] = None
    plagiarism_result: Optional[str] = None
    report_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class SubmissionDetailOut(SubmissionOut):
    project_title: str
    student_name: str
    student_matric: Optional[str] = None
    department: str
