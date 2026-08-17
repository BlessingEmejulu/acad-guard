"""
User Management API Router.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, Supervisor
from app.models.audit_log import AuditLog
from app.schemas.user import UserOut, UserUpdate, AdminUserCreate, AdminUserUpdate
from app.core.security import get_password_hash
from app.core.dependencies import get_current_user, get_current_admin

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=List[UserOut])
def list_users(
    role: Optional[str] = Query(None, description="Filter by role (student, supervisor, admin)"),
    search: Optional[str] = Query(None, description="Search by name, email, or matric number"),
    department: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List users with filtering (Accessible to all authenticated users for directory lookups)."""
    query = db.query(User)

    if role:
        query = query.filter(User.role == role.lower())
    if department:
        query = query.filter(User.department == department)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if search:
        search_filter = f"%{search.strip()}%"
        query = query.filter(
            (User.full_name.ilike(search_filter)) |
            (User.email.ilike(search_filter)) |
            (User.matric_number.ilike(search_filter))
        )

    users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single user profile by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def admin_create_user(
    data: AdminUserCreate,
    request: Request,
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin endpoint to create any user role."""
    existing = db.query(User).filter(User.email == data.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    new_user = User(
        full_name=data.full_name.strip(),
        email=data.email.lower().strip(),
        password_hash=get_password_hash(data.password),
        role=data.role.lower(),
        department=data.department,
        matric_number=data.matric_number if data.role == "student" else None,
        phone=data.phone,
        is_active=data.is_active
    )
    db.add(new_user)
    db.flush()

    if data.role == "supervisor":
        sup = Supervisor(
            user_id=new_user.id,
            staff_id=data.staff_id,
            department=data.department
        )
        db.add(sup)

    audit = AuditLog(
        user_id=admin_user.id,
        action="ADMIN_CREATE_USER",
        description=f"Admin created user {new_user.email} with role {new_user.role}",
        ip_address=request.client.host if request.client else None
    )
    db.add(audit)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update profile information (own profile or admin)."""
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only update your own profile.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if data.full_name is not None:
        user.full_name = data.full_name.strip()
    if data.department is not None:
        user.department = data.department
    if data.phone is not None:
        user.phone = data.phone
    if data.matric_number is not None and user.role == "student":
        user.matric_number = data.matric_number

    if user.supervisor_profile and data.specialization is not None:
        user.supervisor_profile.specialization = data.specialization
    if user.supervisor_profile and data.staff_id is not None:
        user.supervisor_profile.staff_id = data.staff_id

    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    request: Request,
    admin_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin endpoint to delete a user."""
    if admin_user.id == user_id:
        raise HTTPException(status_code=400, detail="Administrators cannot delete their own account.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    email = user.email
    db.delete(user)

    audit = AuditLog(
        user_id=admin_user.id,
        action="ADMIN_DELETE_USER",
        description=f"Admin deleted user {email} (ID: {user_id})",
        ip_address=request.client.host if request.client else None
    )
    db.add(audit)
    db.commit()
    return {"message": f"User '{email}' deleted successfully."}
