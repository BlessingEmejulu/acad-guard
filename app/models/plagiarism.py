"""
Plagiarism Reports and Similarity Matches Database Models.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class PlagiarismReport(Base):
    __tablename__ = "plagiarism_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    submission_id = Column(Integer, ForeignKey("submissions.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    similarity_score = Column(Float, nullable=False, default=0.0) # Percentage e.g. 14.5
    result = Column(String(50), nullable=False) # Original, Low Similarity, Needs Review, Potential Plagiarism
    matched_documents_count = Column(Integer, default=0, nullable=False)
    processing_time = Column(Float, default=0.0, nullable=False) # In seconds
    total_words = Column(Integer, default=0, nullable=True)
    total_unique_words = Column(Integer, default=0, nullable=True)
    method_summary = Column(Text, nullable=True) # JSON or details of TF-IDF / Cosine / N-gram calculations
    review_status = Column(String(50), default="Pending Review", nullable=False) # Pending Review, Cleared, Flagged, Action Taken
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    submission = relationship("Submission", back_populates="plagiarism_report")
    matches = relationship("SimilarityMatch", back_populates="report", cascade="all, delete-orphan", order_by="SimilarityMatch.similarity_score.desc()")

class SimilarityMatch(Base):
    __tablename__ = "similarity_matches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    report_id = Column(Integer, ForeignKey("plagiarism_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    matched_submission_id = Column(Integer, ForeignKey("submissions.id", ondelete="SET NULL"), nullable=True, index=True)
    similarity_score = Column(Float, nullable=False) # Percentage e.g. 64.2
    matched_text = Column(Text, nullable=True) # Matched phrases/paragraphs formatted as JSON or excerpt
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    report = relationship("PlagiarismReport", back_populates="matches")
    matched_submission = relationship("Submission", foreign_keys=[matched_submission_id])
