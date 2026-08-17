"""
Plagiarism and Similarity Report Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict

class MatchedSnippet(BaseModel):
    phrase: str
    match_type: str # exact, fuzzy, paraphrased
    source_index: Optional[int] = None

class SimilarityMatchOut(BaseModel):
    id: int
    matched_submission_id: Optional[int] = None
    matched_project_title: str
    matched_student_name: str
    matched_academic_session: str
    similarity_score: float
    matched_snippets: List[str] = [] # Highlighted phrases / sentences
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PlagiarismReportOut(BaseModel):
    id: int
    submission_id: int
    project_id: int
    project_title: str
    student_name: str
    student_matric: Optional[str] = None
    department: str
    academic_session: str
    original_filename: str
    submission_version: int
    submission_date: datetime
    similarity_score: float
    result: str # Original, Low Similarity, Needs Review, Potential Plagiarism
    matched_documents_count: int
    processing_time: float
    total_words: Optional[int] = None
    total_unique_words: Optional[int] = None
    review_status: str
    created_at: datetime
    matches: List[SimilarityMatchOut] = []
    extracted_text_preview: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PlagiarismCheckRequest(BaseModel):
    submission_id: int
    force_recheck: bool = False

class PlagiarismReviewAction(BaseModel):
    review_status: str # "Cleared", "Flagged", "Action Taken"
    comments: Optional[str] = None
