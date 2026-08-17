"""
Projects Management API Router.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.project import Project
from app.models.user import User, Supervisor
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut, ProjectDetailOut
from app.core.dependencies import get_current_user
from app.services.project_service import create_project, update_project, format_project_dict

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_new_project(
    data: ProjectCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new academic project. (Students create their own; Admins can assign)."""
    client_ip = request.client.host if request.client else None
    student_id = current_user.id
    project = create_project(db=db, student_id=student_id, data=data, ip_address=client_ip)
    return format_project_dict(project)

@router.get("", response_model=List[ProjectOut])
def list_projects(
    status: Optional[str] = Query(None, description="Filter by status"),
    department: Optional[str] = Query(None),
    academic_session: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    supervisor_id: Optional[int] = Query(None),
    student_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None, description="Search project title or description"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List projects based on role:
    - Student: sees their own projects by default.
    - Supervisor: sees projects assigned to them or filtered.
    - Admin: sees all projects across the institution.
    """
    query = db.query(Project)

    if current_user.role == "student":
        query = query.filter(Project.student_id == current_user.id)
    elif current_user.role == "supervisor":
        if current_user.supervisor_profile:
            query = query.filter(
                (Project.supervisor_id == current_user.supervisor_profile.id) |
                (Project.department == current_user.department)
            )
    
    # Optional filters
    if status:
        query = query.filter(Project.status == status)
    if department:
        query = query.filter(Project.department == department)
    if academic_session:
        query = query.filter(Project.academic_session == academic_session)
    if category:
        query = query.filter(Project.category == category)
    if supervisor_id:
        query = query.filter(Project.supervisor_id == supervisor_id)
    if student_id and current_user.role in ["supervisor", "admin"]:
        query = query.filter(Project.student_id == student_id)
    if search:
        search_filter = f"%{search.strip()}%"
        query = query.filter(
            (Project.title.ilike(search_filter)) |
            (Project.description.ilike(search_filter))
        )

    projects = query.order_by(Project.updated_at.desc()).all()
    return [format_project_dict(p) for p in projects]

@router.get("/{project_id}", response_model=ProjectDetailOut)
def get_project_details(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive project details including submission history and feedback."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    if current_user.role == "student" and project.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")

    formatted = format_project_dict(project)
    
    # Format submissions brief list
    submissions_list = []
    for sub in project.submissions:
        score = sub.plagiarism_report.similarity_score if sub.plagiarism_report else None
        res = sub.plagiarism_report.result if sub.plagiarism_report else None
        submissions_list.append({
            "id": sub.id,
            "version": sub.version,
            "original_filename": sub.original_filename,
            "file_type": sub.file_type,
            "file_size": sub.file_size,
            "submission_status": sub.submission_status,
            "submitted_at": sub.submitted_at,
            "similarity_score": score,
            "plagiarism_result": res
        })

    formatted["submissions"] = submissions_list
    formatted["feedbacks_count"] = len(project.feedbacks)
    return formatted

@router.put("/{project_id}", response_model=ProjectOut)
def update_existing_project(
    project_id: int,
    data: ProjectUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update project details or status."""
    client_ip = request.client.host if request.client else None
    project = update_project(db=db, project_id=project_id, current_user=current_user, data=data, ip_address=client_ip)
    return format_project_dict(project)

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a project (Owner or Admin)."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    if current_user.role != "admin" and project.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this project.")

    title = project.title
    db.delete(project)
    db.commit()
    return {"message": f"Project '{title}' deleted successfully."}
