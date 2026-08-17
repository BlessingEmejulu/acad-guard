"""
Authentication and User Service.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, Supervisor
from app.models.audit_log import AuditLog
from app.core.security import verify_password, get_password_hash, create_access_token
from app.schemas.auth import UserRegister, UserLogin

def register_user(db: Session, data: UserRegister, ip_address: Optional[str] = None) -> User:
    """Register a new student or supervisor user."""
    # Check if email exists
    existing = db.query(User).filter(User.email == data.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # Check matric number if student
    if data.role == "student" and data.matric_number:
        matric_check = db.query(User).filter(User.matric_number == data.matric_number).first()
        if matric_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A student with this matriculation number already exists."
            )

    role = data.role.lower()
    if role not in ["student", "supervisor"]:
        role = "student"

    user = User(
        full_name=data.full_name.strip(),
        email=data.email.lower().strip(),
        password_hash=get_password_hash(data.password),
        role=role,
        department=data.department,
        matric_number=data.matric_number if role == "student" else None,
        phone=data.phone,
        is_active=True
    )
    db.add(user)
    db.flush()

    # If supervisor, create Supervisor profile entry
    if role == "supervisor":
        sup_profile = Supervisor(
            user_id=user.id,
            staff_id=data.staff_id,
            department=data.department
        )
        db.add(sup_profile)

    # Log audit
    audit = AuditLog(
        user_id=user.id,
        action="USER_REGISTER",
        description=f"New user registered as {role}: {user.email}",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, data: UserLogin, ip_address: Optional[str] = None) -> Dict[str, Any]:
    """Authenticate a user by email and password and return access token."""
    user = db.query(User).filter(User.email == data.email.lower().strip()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact an administrator."
        )

    # Create access token
    access_token = create_access_token(subject=user.id, role=user.role)

    # Log audit
    audit = AuditLog(
        user_id=user.id,
        action="USER_LOGIN",
        description=f"User logged in ({user.role}): {user.email}",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "department": user.department,
            "matric_number": user.matric_number,
            "supervisor_id": user.supervisor_profile.id if user.supervisor_profile else None
        }
    }
