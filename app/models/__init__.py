"""
Database models export.
"""
from app.models.user import User, Supervisor
from app.models.project import Project
from app.models.submission import Submission
from app.models.plagiarism import PlagiarismReport, SimilarityMatch
from app.models.feedback import Feedback
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.models.setting import SystemSetting

__all__ = [
    "User",
    "Supervisor",
    "Project",
    "Submission",
    "PlagiarismReport",
    "SimilarityMatch",
    "Feedback",
    "Notification",
    "AuditLog",
    "SystemSetting"
]
