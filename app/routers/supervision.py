"""
Supervision and Feedback Management API Router.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, Supervisor
from app.models.project import Project
from app.models.feedback import Feedback
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.schemas.user import SupervisorListOut
from app.schemas.feedback import FeedbackCreate, FeedbackOut, ProjectReviewRequest
from app.schemas.project import ProjectOut
from app.core.dependencies import get_current_user, get_current_supervisor, get_current_admin
from app.services.project_service import format_project_dict

router = APIRouter(tags=["Supervision"])

@router.get("/supervisors", response_model=List[SupervisorListOut])
def list_supervisors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all registered academic supervisors with their active student counts."""
    supervisors = db.query(Supervisor).join(User).all()
    results = []
    for sup in supervisors:
        assigned_count = db.query(Project).filter(Project.supervisor_id == sup.id).count()
        results.append({
            "id": sup.id,
            "user_id": sup.user_id,
            "full_name": sup.user.full_name,
            "email": sup.user.email,
            "department": sup.department or sup.user.department,
            "staff_id": sup.staff_id,
            "specialization": sup.specialization,
            "max_students": sup.max_students,
            "assigned_count": assigned_count
        })
    return results

@router.post("/projects/{project_id}/assign-supervisor", response_model=ProjectOut)
def assign_supervisor(
    project_id: int,
    supervisor_id: int,
    request: Request,
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin endpoint to assign or re-assign a project supervisor."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    supervisor = db.query(Supervisor).filter(Supervisor.id == supervisor_id).first()
    if not supervisor:
        raise HTTPException(status_code=404, detail="Supervisor not found.")

    project.supervisor_id = supervisor.id
    db.commit()

    # Create notifications
    notif_student = Notification(
        user_id=project.student_id,
        title="Supervisor Assigned",
        message=f"{supervisor.user.full_name} has been assigned as supervisor for '{project.title}'.",
        type="info",
        link=f"/student/projects/{project.id}"
    )
    db.add(notif_student)

    notif_sup = Notification(
        user_id=supervisor.user_id,
        title="New Supervised Project Assigned",
        message=f"You have been assigned to supervise project '{project.title}' by {project.student.full_name}.",
        type="info",
        link=f"/supervisor/projects/{project.id}"
    )
    db.add(notif_sup)

    audit = AuditLog(
        user_id=admin_user.id,
        action="SUPERVISOR_ASSIGN",
        description=f"Assigned supervisor {supervisor.user.full_name} to project #{project.id} ({project.title})",
        ip_address=request.client.host if request.client else None
    )
    db.add(audit)
    db.commit()

    return format_project_dict(project)

@router.put("/projects/{project_id}/review", response_model=ProjectOut)
def review_project_submission(
    project_id: int,
    data: ProjectReviewRequest,
    request: Request,
    current_user: User = Depends(get_current_supervisor),
    db: Session = Depends(get_db)
):
    """
    Supervisor or Admin reviews project submission:
    Action: Approved, Rejected, Revision Required
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    # Validate action
    valid_actions = ["Approved", "Rejected", "Revision Required"]
    if data.action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Invalid review action. Must be one of: {', '.join(valid_actions)}")

    # Check permission if supervisor
    if current_user.role == "supervisor":
        if not project.supervisor or project.supervisor.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You are not assigned to supervise this project.")

    project.status = data.action

    # Add feedback record
    feedback = Feedback(
        project_id=project.id,
        supervisor_id=project.supervisor_id or 1,
        feedback_text=data.feedback_text,
        status=data.action
    )
    db.add(feedback)

    # Notify student
    notif_type = "success" if data.action == "Approved" else ("warning" if data.action == "Revision Required" else "error")
    notif = Notification(
        user_id=project.student_id,
        title=f"Project Review: {data.action}",
        message=f"Supervisor reviewed your project '{project.title}': {data.action}. Feedback: {data.feedback_text[:120]}...",
        type=notif_type,
        link=f"/student/projects/{project.id}"
    )
    db.add(notif)

    audit = AuditLog(
        user_id=current_user.id,
        action="SUPERVISOR_REVIEW",
        description=f"Reviewed project #{project.id} with status '{data.action}'",
        ip_address=request.client.host if request.client else None
    )
    db.add(audit)
    db.commit()

    return format_project_dict(project)

@router.post("/projects/{project_id}/feedback", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
def add_feedback(
    project_id: int,
    data: FeedbackCreate,
    current_user: User = Depends(get_current_supervisor),
    db: Session = Depends(get_db)
):
    """Add general feedback comment to a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    sup_id = project.supervisor_id
    if not sup_id:
        if current_user.supervisor_profile:
            sup_id = current_user.supervisor_profile.id
        else:
            sup_id = 1

    feedback = Feedback(
        project_id=project.id,
        supervisor_id=sup_id,
        feedback_text=data.feedback_text,
        status=data.status
    )
    db.add(feedback)

    notif = Notification(
        user_id=project.student_id,
        title="New Feedback Received",
        message=f"New feedback received on project '{project.title}': {data.feedback_text[:100]}...",
        type="info",
        link=f"/student/projects/{project.id}"
    )
    db.add(notif)
    db.commit()
    db.refresh(feedback)

    return {
        "id": feedback.id,
        "project_id": feedback.project_id,
        "supervisor_id": feedback.supervisor_id,
        "supervisor_name": current_user.full_name,
        "feedback_text": feedback.feedback_text,
        "status": feedback.status,
        "created_at": feedback.created_at
    }

@router.get("/projects/{project_id}/feedback", response_model=List[FeedbackOut])
def get_project_feedback(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all feedback history for a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    feedbacks = db.query(Feedback).filter(Feedback.project_id == project_id).order_by(Feedback.created_at.desc()).all()
    results = []
    for f in feedbacks:
        sup_name = f.supervisor.user.full_name if f.supervisor and f.supervisor.user else "Faculty Supervisor"
        results.append({
            "id": f.id,
            "project_id": f.project_id,
            "supervisor_id": f.supervisor_id,
            "supervisor_name": sup_name,
            "feedback_text": f.feedback_text,
            "status": f.status,
            "created_at": f.created_at
        })
    return results
