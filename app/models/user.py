"""
User and Supervisor SQLAlchemy Database Models.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="student", index=True) # "student", "supervisor", "admin"
    department = Column(String(100), nullable=True)
    matric_number = Column(String(50), nullable=True, unique=True, index=True)
    phone = Column(String(30), nullable=True)
    profile_image = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    supervisor_profile = relationship("Supervisor", back_populates="user", uselist=False, cascade="all, delete-orphan")
    owned_projects = relationship("Project", back_populates="student", foreign_keys="Project.student_id", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="submitter", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

class Supervisor(Base):
    __tablename__ = "supervisors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    staff_id = Column(String(50), unique=True, index=True, nullable=True)
    department = Column(String(100), nullable=True)
    specialization = Column(String(255), nullable=True)
    max_students = Column(Integer, default=10, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="supervisor_profile")
    supervised_projects = relationship("Project", back_populates="supervisor", foreign_keys="Project.supervisor_id")
    feedbacks = relationship("Feedback", back_populates="supervisor", cascade="all, delete-orphan")
