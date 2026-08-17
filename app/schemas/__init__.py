"""
Schemas package exports.
"""
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, ForgotPasswordRequest, ChangePasswordRequest
from app.schemas.user import UserOut, UserUpdate, AdminUserCreate, AdminUserUpdate, SupervisorListOut
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut, ProjectDetailOut
from app.schemas.submission import SubmissionOut, SubmissionDetailOut
from app.schemas.plagiarism import (
    PlagiarismReportOut,
    SimilarityMatchOut,
    PlagiarismCheckRequest,
    PlagiarismReviewAction
)
from app.schemas.feedback import FeedbackCreate, FeedbackOut, ProjectReviewRequest
from app.schemas.dashboard import (
    NotificationOut,
    AuditLogOut,
    SystemSettingOut,
    SystemSettingUpdate,
    StudentDashboardOut,
    SupervisorDashboardOut,
    AdminDashboardOut
)

__all__ = [
    "UserRegister", "UserLogin", "TokenResponse", "ForgotPasswordRequest", "ChangePasswordRequest",
    "UserOut", "UserUpdate", "AdminUserCreate", "AdminUserUpdate", "SupervisorListOut",
    "ProjectCreate", "ProjectUpdate", "ProjectOut", "ProjectDetailOut",
    "SubmissionOut", "SubmissionDetailOut",
    "PlagiarismReportOut", "SimilarityMatchOut", "PlagiarismCheckRequest", "PlagiarismReviewAction",
    "FeedbackCreate", "FeedbackOut", "ProjectReviewRequest",
    "NotificationOut", "AuditLogOut", "SystemSettingOut", "SystemSettingUpdate",
    "StudentDashboardOut", "SupervisorDashboardOut", "AdminDashboardOut"
]
