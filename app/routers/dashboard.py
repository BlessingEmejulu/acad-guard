"""
Dashboard Statistics and Metrics API Router.
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import APIRouter, Depends
from app.database import get_db
from app.models.user import User, Supervisor
from app.models.project import Project
from app.models.submission import Submission
from app.models.plagiarism import PlagiarismReport
from app.models.feedback import Feedback
from app.models.audit_log import AuditLog
from app.schemas.dashboard import StudentDashboardOut, SupervisorDashboardOut, AdminDashboardOut
from app.core.dependencies import get_current_user, get_current_supervisor, get_current_admin
from app.services.project_service import format_project_dict

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/student", response_model=StudentDashboardOut)
def get_student_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve statistics and recent activity for the student dashboard."""
    student_id = current_user.id
    projects = db.query(Project).filter(Project.student_id == student_id).all()
    
    total_projects = len(projects)
    submitted_projects = sum(1 for p in projects if p.status in ["Submitted", "Under Review"])
    under_review = sum(1 for p in projects if p.status == "Under Review")
    approved = sum(1 for p in projects if p.status in ["Approved", "Completed"])
    revision_req = sum(1 for p in projects if p.status == "Revision Required")

    # Latest similarity score
    latest_submission = (
        db.query(Submission)
        .filter(Submission.submitted_by == student_id)
        .order_by(Submission.submitted_at.desc())
        .first()
    )
    latest_score = None
    if latest_submission and latest_submission.plagiarism_report:
        latest_score = latest_submission.plagiarism_report.similarity_score

    # Recent projects
    recent_projects_orm = (
        db.query(Project)
        .filter(Project.student_id == student_id)
        .order_by(Project.updated_at.desc())
        .limit(5)
        .all()
    )
    recent_projects = [format_project_dict(p) for p in recent_projects_orm]

    # Recent feedback
    recent_feedback_orm = (
        db.query(Feedback)
        .join(Project)
        .filter(Project.student_id == student_id)
        .order_by(Feedback.created_at.desc())
        .limit(5)
        .all()
    )
    recent_feedback = []
    for fb in recent_feedback_orm:
        recent_feedback.append({
            "id": fb.id,
            "project_id": fb.project_id,
            "project_title": fb.project.title,
            "supervisor_name": fb.supervisor.user.full_name if fb.supervisor and fb.supervisor.user else "Supervisor",
            "feedback_text": fb.feedback_text,
            "status": fb.status,
            "created_at": fb.created_at
        })

    return {
        "total_projects": total_projects,
        "submitted_projects": submitted_projects,
        "projects_under_review": under_review,
        "approved_projects": approved,
        "revision_required_projects": revision_req,
        "latest_similarity_score": latest_score,
        "recent_projects": recent_projects,
        "recent_feedback": recent_feedback
    }

@router.get("/supervisor", response_model=SupervisorDashboardOut)
def get_supervisor_dashboard(
    current_user: User = Depends(get_current_supervisor),
    db: Session = Depends(get_db)
):
    """Retrieve statistics and pending reviews for the supervisor dashboard."""
    sup_profile = current_user.supervisor_profile
    sup_id = sup_profile.id if sup_profile else 0

    projects = db.query(Project).filter(
        (Project.supervisor_id == sup_id) |
        (Project.department == current_user.department)
    ).all()

    assigned_students_count = db.query(Project.student_id).filter(Project.supervisor_id == sup_id).distinct().count()
    total_projects = len(projects)
    pending_reviews = sum(1 for p in projects if p.status in ["Submitted", "Under Review"])
    approved = sum(1 for p in projects if p.status in ["Approved", "Completed"])
    revision_req = sum(1 for p in projects if p.status == "Revision Required")

    # Status distribution
    status_dist = {}
    for p in projects:
        status_dist[p.status] = status_dist.get(p.status, 0) + 1

    # Recent submissions assigned
    recent_subs = (
        db.query(Submission)
        .join(Project)
        .filter(Project.supervisor_id == sup_id)
        .order_by(Submission.submitted_at.desc())
        .limit(6)
        .all()
    )
    recent_submissions = []
    for s in recent_subs:
        score = s.plagiarism_report.similarity_score if s.plagiarism_report else None
        res = s.plagiarism_report.result if s.plagiarism_report else None
        recent_submissions.append({
            "id": s.id,
            "project_id": s.project_id,
            "project_title": s.project.title,
            "student_name": s.project.student.full_name if s.project.student else "Student",
            "version": s.version,
            "original_filename": s.original_filename,
            "submission_status": s.submission_status,
            "submitted_at": s.submitted_at,
            "similarity_score": score,
            "plagiarism_result": res,
            "report_id": s.plagiarism_report.id if s.plagiarism_report else None
        })

    return {
        "assigned_students": assigned_students_count,
        "total_projects": total_projects,
        "pending_reviews": pending_reviews,
        "approved_projects": approved,
        "revision_required": revision_req,
        "recent_submissions": recent_submissions,
        "project_status_distribution": status_dist
    }

@router.get("/admin", response_model=AdminDashboardOut)
def get_admin_dashboard(
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Retrieve comprehensive system metrics and Chart.js datasets for the administrator dashboard."""
    total_users = db.query(User).count()
    total_students = db.query(User).filter(User.role == "student").count()
    total_supervisors = db.query(User).filter(User.role == "supervisor").count()
    total_projects = db.query(Project).count()
    total_submissions = db.query(Submission).count()
    pending_reviews = db.query(Project).filter(Project.status.in_(["Submitted", "Under Review"])).count()

    # Average similarity
    avg_score = db.query(func.avg(PlagiarismReport.similarity_score)).scalar() or 0.0
    avg_score = round(float(avg_score), 2)

    # Status distribution
    projects = db.query(Project.status).all()
    status_dist = {
        "Draft": 0, "Submitted": 0, "Under Review": 0,
        "Approved": 0, "Rejected": 0, "Revision Required": 0, "Completed": 0
    }
    for p in projects:
        st = p[0]
        status_dist[st] = status_dist.get(st, 0) + 1

    # Similarity distribution
    reports = db.query(PlagiarismReport.similarity_score).all()
    sim_dist = {
        "0-19% (Original)": 0,
        "20-39% (Low)": 0,
        "40-59% (Moderate)": 0,
        "60-100% (High/Potential Plagiarism)": 0
    }
    for r in reports:
        score = r[0]
        if score < 20:
            sim_dist["0-19% (Original)"] += 1
        elif score < 40:
            sim_dist["20-39% (Low)"] += 1
        elif score < 60:
            sim_dist["40-59% (Moderate)"] += 1
        else:
            sim_dist["60-100% (High/Potential Plagiarism)"] += 1

    # Recent activities (audit logs)
    activities_orm = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(8).all()
    recent_activities = []
    for a in activities_orm:
        recent_activities.append({
            "id": a.id,
            "action": a.action,
            "description": a.description,
            "user_name": a.user.full_name if a.user else "System",
            "ip_address": a.ip_address,
            "created_at": a.created_at
        })

    # Submission trends (monthly/session aggregations)
    departments = ["Computer Science", "Software Engineering", "Cyber Security", "Information Technology"]
    dept_submissions = []
    for d in departments:
        cnt = db.query(Submission).join(Project).filter(Project.department == d).count()
        dept_submissions.append({"department": d, "count": cnt})

    return {
        "total_users": total_users,
        "total_students": total_students,
        "total_supervisors": total_supervisors,
        "total_projects": total_projects,
        "total_submissions": total_submissions,
        "average_similarity": avg_score,
        "pending_reviews": pending_reviews,
        "status_distribution": status_dist,
        "similarity_distribution": sim_dist,
        "recent_activities": recent_activities,
        "submission_trends": dept_submissions
    }
