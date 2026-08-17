"""
User and Supervisor Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict

class SupervisorOutBrief(BaseModel):
    id: int
    staff_id: Optional[str] = None
    department: Optional[str] = None
    specialization: Optional[str] = None
    max_students: int = 10
    
    model_config = ConfigDict(from_attributes=True)

class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    department: Optional[str] = None
    matric_number: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None
    is_active: bool
    created_at: datetime
    supervisor_profile: Optional[SupervisorOutBrief] = None

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    matric_number: Optional[str] = None
    staff_id: Optional[str] = None
    specialization: Optional[str] = None

class AdminUserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str # student, supervisor, admin
    department: Optional[str] = None
    matric_number: Optional[str] = None
    staff_id: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True

class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    department: Optional[str] = None
    matric_number: Optional[str] = None
    staff_id: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class SupervisorListOut(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    department: Optional[str] = None
    staff_id: Optional[str] = None
    specialization: Optional[str] = None
    max_students: int
    assigned_count: int

    model_config = ConfigDict(from_attributes=True)
