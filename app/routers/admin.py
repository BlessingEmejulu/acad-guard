"""
Admin Management and System Configuration API Router.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.setting import SystemSetting
from app.models.submission import Submission
from app.schemas.dashboard import AuditLogOut, SystemSettingOut, SystemSettingUpdate
from app.core.dependencies import get_current_admin
from app.services.plagiarism.engine import PlagiarismEngine

router = APIRouter(prefix="/admin", tags=["Admin Operations"])

@router.get("/audit-logs", response_model=List[AuditLogOut])
def get_audit_logs(
    action: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    limit: int = 100,
    offset: int = 0,
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List system audit logs with user info and timestamps."""
    query = db.query(AuditLog)

    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    results = []
    for l in logs:
        results.append({
            "id": l.id,
            "user_id": l.user_id,
            "user_name": l.user.full_name if l.user else "System",
            "user_email": l.user.email if l.user else None,
            "action": l.action,
            "description": l.description,
            "ip_address": l.ip_address,
            "created_at": l.created_at
        })
    return results

@router.get("/settings", response_model=List[SystemSettingOut])
def get_system_settings(
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List institution system settings."""
    settings_list = db.query(SystemSetting).all()
    return settings_list

@router.put("/settings/{key}", response_model=SystemSettingOut)
def update_system_setting(
    key: str,
    data: SystemSettingUpdate,
    request: Request,
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update institution system configuration setting."""
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not setting:
        setting = SystemSetting(key=key, value=data.value, description=f"Custom setting for {key}")
        db.add(setting)
    else:
        setting.value = data.value

    audit = AuditLog(
        user_id=admin_user.id,
        action="SETTING_UPDATE",
        description=f"Updated system setting '{key}' to '{data.value}'",
        ip_address=request.client.host if request.client else None
    )
    db.add(audit)
    db.commit()
    db.refresh(setting)
    return setting

@router.post("/recheck-all-plagiarism")
def recheck_all_submissions(
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Re-run plagiarism similarity engine on all existing submissions against current corpus."""
    submissions = db.query(Submission).order_by(Submission.id.asc()).all()
    count = 0
    for sub in submissions:
        try:
            PlagiarismEngine.run_check(submission_id=sub.id, db=db, force_recheck=True)
            count += 1
        except Exception:
            continue

    audit = AuditLog(
        user_id=admin_user.id,
        action="BULK_PLAGIARISM_RECHECK",
        description=f"Admin initiated bulk plagiarism re-check for {count} submissions."
    )
    db.add(audit)
    db.commit()

    return {"message": f"Successfully re-analyzed {count} submissions against current academic corpus."}
