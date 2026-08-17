"""
Project Management Service.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.project import Project
from app.models.user import User, Supervisor
from app.models.submission import Submission
from app.models.audit_log import AuditLog
from app.schemas.project import ProjectCreate, ProjectUpdate

def create_project(db: Session, student_id: int, data: ProjectCreate, ip_address: Optional[str] = None) -> Project:
    """Create a new academic project for a student."""
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    # Validate supervisor if specified
    if data.supervisor_id:
        supervisor = db.query(Supervisor).filter(Supervisor.id == data.supervisor_id).first()
        if not supervisor:
            raise HTTPException(status_code=404, detail="Selected supervisor not found.")

    project = Project(
        title=data.title.strip(),
        description=data.description.strip() if data.description else None,
        category=data.category,
        department=data.department or student.department or "Computer Science",
        academic_session=data.academic_session,
        student_id=student_id,
        supervisor_id=data.supervisor_id,
        status="Draft"
    )
    db.add(project)
    db.flush()

    audit = AuditLog(
        user_id=student_id,
        action="PROJECT_CREATE",
        description=f"Created project '{project.title}' (ID: {project.id})",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()
    db.refresh(project)
    return project

def update_project(db: Session, project_id: int, current_user: User, data: ProjectUpdate, ip_address: Optional[str] = None) -> Project:
    """Update project details or status."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    # Check permission
    if current_user.role == "student" and project.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to edit this project.")

    if data.title is not None:
        project.title = data.title.strip()
    if data.description is not None:
        project.description = data.description.strip()
    if data.category is not None:
        project.category = data.category
    if data.department is not None:
        project.department = data.department
    if data.academic_session is not None:
        project.academic_session = data.academic_session

    # Supervisor or Admin can change supervisor or status
    if current_user.role in ["supervisor", "admin"]:
        if data.supervisor_id is not None:
            project.supervisor_id = data.supervisor_id
        if data.status is not None:
            valid_statuses = ["Draft", "Submitted", "Under Review", "Approved", "Rejected", "Revision Required", "Completed"]
            if data.status not in valid_statuses:
                raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
            project.status = data.status

    audit = AuditLog(
        user_id=current_user.id,
        action="PROJECT_UPDATE",
        description=f"Updated project '{project.title}' (ID: {project.id})",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()
    db.refresh(project)
    return project

def format_project_dict(project: Project) -> Dict[str, Any]:
    """Helper to convert Project ORM to dictionary format with student and supervisor details."""
    latest_sub = project.submissions[0] if project.submissions else None
    latest_score = None
    latest_sub_id = None
    if latest_sub:
        latest_sub_id = latest_sub.id
        if latest_sub.plagiarism_report:
            latest_score = latest_sub.plagiarism_report.similarity_score

    supervisor_info = None
    if project.supervisor and project.supervisor.user:
        supervisor_info = {
            "id": project.supervisor.id,
            "staff_id": project.supervisor.staff_id,
            "full_name": project.supervisor.user.full_name,
            "email": project.supervisor.user.email
        }

    student_info = None
    if project.student:
        student_info = {
            "id": project.student.id,
            "full_name": project.student.full_name,
            "email": project.student.email,
            "matric_number": project.student.matric_number,
            "department": project.student.department
        }

    return {
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "category": project.category,
        "department": project.department,
        "academic_session": project.academic_session,
        "student_id": project.student_id,
        "supervisor_id": project.supervisor_id,
        "status": project.status,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "student": student_info,
        "supervisor_info": supervisor_info,
        "submissions_count": len(project.submissions),
        "latest_similarity_score": latest_score,
        "latest_submission_id": latest_sub_id
    }
