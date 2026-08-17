"""
Notification, Audit Log, Dashboard, and System Settings Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

# Notifications
class NotificationOut(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str # info, success, warning, error
    link: Optional[str] = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Audit Log
class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    action: str
    description: str
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# System Settings
class SystemSettingOut(BaseModel):
    id: int
    key: str
    value: str
    description: Optional[str] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SystemSettingUpdate(BaseModel):
    value: str

# Dashboard Statistics
class StudentDashboardOut(BaseModel):
    total_projects: int
    submitted_projects: int
    projects_under_review: int
    approved_projects: int
    revision_required_projects: int
    latest_similarity_score: Optional[float] = None
    recent_projects: List[Dict[str, Any]] = []
    recent_feedback: List[Dict[str, Any]] = []

class SupervisorDashboardOut(BaseModel):
    assigned_students: int
    total_projects: int
    pending_reviews: int
    approved_projects: int
    revision_required: int
    recent_submissions: List[Dict[str, Any]] = []
    project_status_distribution: Dict[str, int] = {}

class AdminDashboardOut(BaseModel):
    total_users: int
    total_students: int
    total_supervisors: int
    total_projects: int
    total_submissions: int
    average_similarity: float
    pending_reviews: int
    status_distribution: Dict[str, int] = {}
    similarity_distribution: Dict[str, int] = {} # e.g. {"0-19%": 12, "20-39%": 5, "40-59%": 2, "60-100%": 1}
    recent_activities: List[Dict[str, Any]] = []
    submission_trends: List[Dict[str, Any]] = []
