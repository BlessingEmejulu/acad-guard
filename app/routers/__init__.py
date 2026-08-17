"""
Routers package export.
"""
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.projects import router as projects_router
from app.routers.submissions import router as submissions_router
from app.routers.plagiarism import router as plagiarism_router
from app.routers.supervision import router as supervision_router
from app.routers.dashboard import router as dashboard_router
from app.routers.notifications import router as notifications_router
from app.routers.admin import router as admin_router

__all__ = [
    "auth_router",
    "users_router",
    "projects_router",
    "submissions_router",
    "plagiarism_router",
    "supervision_router",
    "dashboard_router",
    "notifications_router",
    "admin_router"
]
