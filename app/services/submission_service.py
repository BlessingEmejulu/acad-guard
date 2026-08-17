"""
Submission and Document Upload Service.
"""
import os
import uuid
import shutil
from typing import Optional, Tuple, Any
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.submission import Submission
from app.models.project import Project
from app.models.user import User
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.services.document_extractor import extract_text_from_file, DocumentExtractionError
from app.services.plagiarism.engine import PlagiarismEngine

def validate_uploaded_file(file: UploadFile) -> Tuple[str, str]:
    """Validate filename extension and sanitize."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename.")

    _, ext = os.path.splitext(file.filename.lower())
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension '{ext}'. Allowed extensions are: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Basic filename sanitization
    clean_original_name = os.path.basename(file.filename)
    return clean_original_name, ext

def handle_document_submission(
    db: Session,
    project_id: int,
    file: UploadFile,
    current_user: User,
    ip_address: Optional[str] = None
) -> Tuple[Submission, Any]:
    """
    Saves document file, records metadata, extracts text, increments version,
    and runs initial plagiarism check automatically.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    # Authorization check
    if current_user.role == "student" and project.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only submit documents to your own projects.")

    original_filename, ext = validate_uploaded_file(file)

    # Determine next version
    latest_sub = db.query(Submission).filter(Submission.project_id == project_id).order_by(Submission.version.desc()).first()
    next_version = (latest_sub.version + 1) if latest_sub else 1

    # Generate secure unique filename
    unique_id = uuid.uuid4().hex
    stored_filename = f"proj_{project_id}_v{next_version}_{unique_id}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, stored_filename)

    # Save file to disk
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")
    finally:
        file.file.close()

    file_size = os.path.getsize(file_path)
    max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
        )

    # Extract text from the saved file
    extracted_text = ""
    try:
        extracted_text, _, _ = extract_text_from_file(file_path, original_filename)
    except DocumentExtractionError as e:
        # Non-fatal during upload, but logged
        extracted_text = ""

    # Create submission record
    submission = Submission(
        project_id=project_id,
        version=next_version,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=file_path,
        file_type=ext,
        file_size=file_size,
        extracted_text=extracted_text,
        submitted_by=current_user.id,
        submission_status="Submitted"
    )
    db.add(submission)
    
    # Update project status
    project.status = "Submitted"
    db.commit()
    db.refresh(submission)

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="DOCUMENT_SUBMIT",
        description=f"Submitted document '{original_filename}' (v{next_version}) for project #{project_id}",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    # Automatically trigger Plagiarism Engine check
    report = PlagiarismEngine.run_check(submission.id, db=db)

    return submission, report
