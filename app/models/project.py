"""
Academic Project SQLAlchemy Database Model.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True) # e.g. Machine Learning, Web Engineering, Information Security, IoT
    department = Column(String(100), nullable=False, index=True)
    academic_session = Column(String(50), nullable=False, index=True) # e.g. 2025/2026
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    supervisor_id = Column(Integer, ForeignKey("supervisors.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(50), nullable=False, default="Draft", index=True) 
    # Allowed statuses: Draft, Submitted, Under Review, Approved, Rejected, Revision Required, Completed

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    student = relationship("User", back_populates="owned_projects", foreign_keys=[student_id])
    supervisor = relationship("Supervisor", back_populates="supervised_projects", foreign_keys=[supervisor_id])
    submissions = relationship("Submission", back_populates="project", cascade="all, delete-orphan", order_by="Submission.version.desc()")
    feedbacks = relationship("Feedback", back_populates="project", cascade="all, delete-orphan", order_by="Feedback.created_at.desc()")
