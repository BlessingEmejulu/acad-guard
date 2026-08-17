"""
Document Submission SQLAlchemy Database Model.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.database import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False) # .pdf, .docx, .txt, etc.
    file_size = Column(BigInteger, nullable=False) # In bytes
    extracted_text = Column(Text, nullable=True) # Normalized extracted text cached for high-speed plagiarism comparison
    submitted_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    submission_status = Column(String(50), default="Submitted", nullable=False) # Submitted, Processing, Checked, Approved, Rejected, Revision Required
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="submissions")
    submitter = relationship("User", back_populates="submissions")
    plagiarism_report = relationship("PlagiarismReport", back_populates="submission", uselist=False, cascade="all, delete-orphan")
