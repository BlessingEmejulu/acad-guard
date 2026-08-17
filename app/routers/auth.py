"""
Authentication API Router.
"""
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, ForgotPasswordRequest, ChangePasswordRequest
from app.schemas.user import UserOut
from app.core.security import get_password_hash, verify_password
from app.core.dependencies import get_current_user
from app.services.auth_service import register_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, request: Request, db: Session = Depends(get_db)):
    """Register a new student or supervisor user."""
    client_ip = request.client.host if request.client else None
    return register_user(db=db, data=data, ip_address=client_ip)

@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Login with email and password to receive a JWT access token."""
    client_ip = request.client.host if request.client else None
    return authenticate_user(db=db, data=data, ip_address=client_ip)

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Get profile information for the currently authenticated user."""
    return current_user

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Logout current user session."""
    return {"message": "Logged out successfully."}

@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change the password of the current user."""
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password does not match.")
    
    current_user.password_hash = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password changed successfully."}

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    """Placeholder endpoint for password reset instructions."""
    return {
        "message": f"If an account exists for {data.email}, password reset instructions have been dispatched. (Demo placeholder)"
    }
