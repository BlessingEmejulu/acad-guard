"""
Submissions and File Uploads API Router.
"""
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.submission import Submission
from app.models.project import Project
from app.models.user import User
from app.schemas.submission import SubmissionOut, SubmissionDetailOut
from app.core.dependencies import get_current_user
from app.services.submission_service import handle_document_submission

router = APIRouter(tags=["Submissions"])

@router.post("/projects/{project_id}/submissions", response_model=SubmissionOut, status_code=status.HTTP_201_CREATED)
async def submit_document(
    project_id: int,
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload an academic document (.pdf, .docx, .txt) for a project.
    Automatically calculates versioning and triggers the Plagiarism Detection Engine.
    """
    client_ip = request.client.host if request.client else None
    submission, report = handle_document_submission(
        db=db,
        project_id=project_id,
        file=file,
        current_user=current_user,
        ip_address=client_ip
    )

    return {
        "id": submission.id,
        "project_id": submission.project_id,
        "version": submission.version,
        "original_filename": submission.original_filename,
        "stored_filename": submission.stored_filename,
        "file_type": submission.file_type,
        "file_size": submission.file_size,
        "submitted_by": submission.submitted_by,
        "submission_status": submission.submission_status,
        "submitted_at": submission.submitted_at,
        "similarity_score": report.similarity_score if report else None,
        "plagiarism_result": report.result if report else None,
        "report_id": report.id if report else None
    }

@router.get("/projects/{project_id}/submissions", response_model=List[SubmissionOut])
def list_project_submissions(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all versioned submissions for a specific project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    if current_user.role == "student" and project.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")

    submissions = db.query(Submission).filter(Submission.project_id == project_id).order_by(Submission.version.desc()).all()
    results = []
    for s in submissions:
        score = s.plagiarism_report.similarity_score if s.plagiarism_report else None
        res = s.plagiarism_report.result if s.plagiarism_report else None
        rep_id = s.plagiarism_report.id if s.plagiarism_report else None
        results.append({
            "id": s.id,
            "project_id": s.project_id,
            "version": s.version,
            "original_filename": s.original_filename,
            "stored_filename": s.stored_filename,
            "file_type": s.file_type,
            "file_size": s.file_size,
            "submitted_by": s.submitted_by,
            "submission_status": s.submission_status,
            "submitted_at": s.submitted_at,
            "similarity_score": score,
            "plagiarism_result": res,
            "report_id": rep_id
        })
    return results

@router.get("/submissions/{submission_id}", response_model=SubmissionDetailOut)
def get_submission_details(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single submission details."""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    project = submission.project
    if current_user.role == "student" and project.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")

    student = project.student
    score = submission.plagiarism_report.similarity_score if submission.plagiarism_report else None
    res = submission.plagiarism_report.result if submission.plagiarism_report else None
    rep_id = submission.plagiarism_report.id if submission.plagiarism_report else None

    return {
        "id": submission.id,
        "project_id": submission.project_id,
        "version": submission.version,
        "original_filename": submission.original_filename,
        "stored_filename": submission.stored_filename,
        "file_type": submission.file_type,
        "file_size": submission.file_size,
        "submitted_by": submission.submitted_by,
        "submission_status": submission.submission_status,
        "submitted_at": submission.submitted_at,
        "similarity_score": score,
        "plagiarism_result": res,
        "report_id": rep_id,
        "project_title": project.title,
        "student_name": student.full_name if student else "Unknown",
        "student_matric": student.matric_number if student else None,
        "department": project.department
    }

@router.get("/submissions/{submission_id}/download")
def download_submission_file(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Protected file download endpoint with original filename disposition."""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    project = submission.project
    if current_user.role == "student" and project.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")

    if not os.path.exists(submission.file_path):
        raise HTTPException(status_code=404, detail="Physical document file missing on server storage.")

    return FileResponse(
        path=submission.file_path,
        filename=submission.original_filename,
        media_type="application/octet-stream"
    )
