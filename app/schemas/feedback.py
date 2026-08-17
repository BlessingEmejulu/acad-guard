"""
Supervisor feedback Pydantic schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class FeedbackCreate(BaseModel):
    feedback_text: str = Field(..., min_length=2)
    status: Optional[str] = None # e.g. "Approved", "Revision Required", "General Comment"

class FeedbackOut(BaseModel):
    id: int
    project_id: int
    supervisor_id: int
    supervisor_name: str
    feedback_text: str
    status: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProjectReviewRequest(BaseModel):
    action: str = Field(..., description="'Approved', 'Rejected', 'Revision Required'")
    feedback_text: str = Field(..., min_length=2)
