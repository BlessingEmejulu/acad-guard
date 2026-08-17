"""
Plagiarism Reports and Similarity Detection API Router.
"""
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.plagiarism import PlagiarismReport, SimilarityMatch
from app.models.submission import Submission
from app.models.project import Project
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.plagiarism import PlagiarismReportOut, PlagiarismCheckRequest, PlagiarismReviewAction
from app.core.dependencies import get_current_user, get_current_supervisor
from app.services.plagiarism.engine import PlagiarismEngine

router = APIRouter(tags=["Plagiarism Detection"])

def format_report_response(report: PlagiarismReport, db: Session) -> dict:
    """Format PlagiarismReport model into comprehensive Pydantic output dictionary."""
    submission = report.submission
    project = submission.project if submission else None
    student = project.student if project else None

    # Load matches with detailed referenced project titles
    matches_list = []
    for match in report.matches:
        matched_sub = match.matched_submission
        matched_proj = matched_sub.project if matched_sub else None
        matched_user = matched_sub.submitter if matched_sub else None

        snippets = []
        if match.matched_text:
            try:
                snippets = json.loads(match.matched_text)
            except Exception:
                snippets = [match.matched_text]

        matches_list.append({
            "id": match.id,
            "matched_submission_id": match.matched_submission_id,
            "matched_project_title": matched_proj.title if matched_proj else "Corpus Document",
            "matched_student_name": matched_user.full_name if matched_user else "Academic Author",
            "matched_academic_session": matched_proj.academic_session if matched_proj else "Archive",
            "similarity_score": match.similarity_score,
            "matched_snippets": snippets,
            "created_at": match.created_at
        })

    text_preview = None
    if submission and submission.extracted_text:
        text_preview = submission.extracted_text[:1200] + ("..." if len(submission.extracted_text) > 1200 else "")

    return {
        "id": report.id,
        "submission_id": report.submission_id,
        "project_id": project.id if project else 0,
        "project_title": project.title if project else "Unknown Project",
        "student_name": student.full_name if student else "Unknown Student",
        "student_matric": student.matric_number if student else None,
        "department": project.department if project else "General",
        "academic_session": project.academic_session if project else "N/A",
        "original_filename": submission.original_filename if submission else "file",
        "submission_version": submission.version if submission else 1,
        "submission_date": submission.submitted_at if submission else report.created_at,
        "similarity_score": report.similarity_score,
        "result": report.result,
        "matched_documents_count": report.matched_documents_count,
        "processing_time": report.processing_time,
        "total_words": report.total_words,
        "total_unique_words": report.total_unique_words,
        "review_status": report.review_status,
        "created_at": report.created_at,
        "matches": matches_list,
        "extracted_text_preview": text_preview
    }

@router.post("/submissions/{submission_id}/check", response_model=PlagiarismReportOut)
def trigger_plagiarism_check(
    submission_id: int,
    force_recheck: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger or re-execute plagiarism similarity analysis on a submission."""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    if current_user.role == "student" and submission.submitted_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")

    report = PlagiarismEngine.run_check(submission_id=submission_id, db=db, force_recheck=force_recheck)
    return format_report_response(report, db)

@router.get("/submissions/{submission_id}/report", response_model=PlagiarismReportOut)
def get_report_by_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve plagiarism analysis report for a specific submission."""
    report = db.query(PlagiarismReport).filter(PlagiarismReport.submission_id == submission_id).first()
    if not report:
        # If no report yet, run it on demand
        report = PlagiarismEngine.run_check(submission_id=submission_id, db=db)

    # Authorization
    if current_user.role == "student" and report.submission.submitted_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")

    return format_report_response(report, db)

@router.get("/reports", response_model=List[PlagiarismReportOut])
def list_reports(
    result: Optional[str] = Query(None, description="Filter by result classification"),
    review_status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None),
    max_score: Optional[float] = Query(None),
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all plagiarism reports with rich filtering (Admin/Supervisor)."""
    query = db.query(PlagiarismReport).join(Submission).join(Project)

    if current_user.role == "student":
        query = query.filter(Submission.submitted_by == current_user.id)
    elif current_user.role == "supervisor" and current_user.supervisor_profile:
        query = query.filter(
            (Project.supervisor_id == current_user.supervisor_profile.id) |
            (Project.department == current_user.department)
        )

    if result:
        query = query.filter(PlagiarismReport.result == result)
    if review_status:
        query = query.filter(PlagiarismReport.review_status == review_status)
    if department:
        query = query.filter(Project.department == department)
    if min_score is not None:
        query = query.filter(PlagiarismReport.similarity_score >= min_score)
    if max_score is not None:
        query = query.filter(PlagiarismReport.similarity_score <= max_score)

    reports = query.order_by(PlagiarismReport.created_at.desc()).offset(offset).limit(limit).all()
    return [format_report_response(r, db) for r in reports]

@router.get("/reports/{report_id}", response_model=PlagiarismReportOut)
def get_report_by_id(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single plagiarism report by report ID."""
    report = db.query(PlagiarismReport).filter(PlagiarismReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    if current_user.role == "student" and report.submission.submitted_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")

    return format_report_response(report, db)

@router.put("/reports/{report_id}/review", response_model=PlagiarismReportOut)
def update_report_review_status(
    report_id: int,
    data: PlagiarismReviewAction,
    current_user: User = Depends(get_current_supervisor),
    db: Session = Depends(get_db)
):
    """Supervisor or Administrator sets review status (Cleared, Flagged, Action Taken)."""
    report = db.query(PlagiarismReport).filter(PlagiarismReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    report.review_status = data.review_status
    audit = AuditLog(
        user_id=current_user.id,
        action="PLAGIARISM_REVIEW_DECISION",
        description=f"Updated report #{report.id} review status to '{data.review_status}'. Comments: {data.comments or 'None'}"
    )
    db.add(audit)
    db.commit()
    db.refresh(report)
    return format_report_response(report, db)

@router.get("/reports/{report_id}/download")
def download_printable_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate professional printable HTML similarity report with styling."""
    report = db.query(PlagiarismReport).filter(PlagiarismReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    if current_user.role == "student" and report.submission.submitted_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")

    data = format_report_response(report, db)

    # Build clean HTML export
    matches_html = ""
    for m in data["matches"]:
        snippets_html = "".join([f"<li><mark style='background:#fef08a; padding:2px 4px;'>\"{s}\"</mark></li>" for s in m["matched_snippets"]]) or "<li>No direct verbatim sentences detected</li>"
        matches_html += f"""
        <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <strong>{m['matched_project_title']}</strong>
                <span style="color:#2563eb; font-weight:bold;">{m['similarity_score']}% Match</span>
            </div>
            <p style="color:#64748b; font-size:13px; margin:0 0 8px 0;">Author: {m['matched_student_name']} | Session: {m['matched_academic_session']}</p>
            <ul style="font-size:13px; color:#334155; margin:0; padding-left:20px;">
                {snippets_html}
            </ul>
        </div>
        """

    badge_color = "#16a34a" if data["similarity_score"] < 20 else ("#f59e0b" if data["similarity_score"] < 40 else "#dc2626")

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AcadGuard Similarity Report - #{report.id}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8fafc; color: #0f172a; padding: 40px; margin: 0; }}
        .container {{ max-width: 800px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 24px; }}
        .score-circle {{ width: 100px; height: 100px; border-radius: 50%; background: {badge_color}; color: white; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; flex-direction: column; }}
        .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 24px; background: #f1f5f9; padding: 16px; border-radius: 8px; font-size: 14px; }}
        @media print {{ body {{ padding: 0; background: white; }} .container {{ box-shadow: none; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1 style="margin:0; font-size:24px; color:#1e293b;">AcadGuard Academic Integrity Report</h1>
                <p style="margin:4px 0 0 0; color:#64748b; font-size:14px;">Report ID: AG-REP-{report.id} | Generated: {report.created_at.strftime('%Y-%m-%d %H:%M UTC')}</p>
            </div>
            <div class="score-circle">
                <span>{data['similarity_score']}%</span>
                <span style="font-size:10px; font-weight:normal;">SIMILARITY</span>
            </div>
        </div>
        <div class="meta-grid">
            <div><strong>Project Title:</strong> {data['project_title']}</div>
            <div><strong>Student Name:</strong> {data['student_name']} ({data['student_matric'] or 'N/A'})</div>
            <div><strong>Department:</strong> {data['department']}</div>
            <div><strong>Academic Session:</strong> {data['academic_session']}</div>
            <div><strong>Original File:</strong> {data['original_filename']} (v{data['submission_version']})</div>
            <div><strong>Classification:</strong> <span style="color:{badge_color}; font-weight:bold;">{data['result']}</span></div>
            <div><strong>Word Count:</strong> {data['total_words']} words</div>
            <div><strong>Processing Time:</strong> {data['processing_time']} seconds</div>
        </div>

        <h3 style="color:#1e293b; border-bottom:1px solid #e2e8f0; padding-bottom:8px;">Matched Academic Submissions ({data['matched_documents_count']})</h3>
        {matches_html if matches_html else '<p style="color:#64748b;">No high-similarity academic document matches detected in the institutional repository.</p>'}

        <div style="margin-top:40px; border-top:1px solid #e2e8f0; padding-top:16px; font-size:12px; color:#94a3b8; text-align:center;">
            AcadGuard Plagiarism & Academic Integrity Engine • Authorized institutional report • Final academic judgement rests with the faculty supervisor.
        </div>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=html_content)
