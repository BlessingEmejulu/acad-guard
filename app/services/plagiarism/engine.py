"""
Academic Plagiarism Detection Engine.
Orchestrates the entire NLP similarity analysis workflow.
"""
import time
import json
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.submission import Submission
from app.models.plagiarism import PlagiarismReport, SimilarityMatch
from app.models.project import Project
from app.models.user import User
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.services.document_extractor import extract_text_from_file, DocumentExtractionError
from app.services.plagiarism.preprocessor import clean_text, tokenize_words
from app.services.plagiarism.fingerprinting import generate_fingerprints, compute_jaccard_similarity, find_matching_snippets
from app.services.plagiarism.vectorizer import compute_tfidf_similarities, calculate_hybrid_score

class PlagiarismEngine:
    """
    Modular Plagiarism Detection Engine.
    Designed for TF-IDF + Fingerprinting with extensibility for Semantic/AI embeddings.
    """

    @staticmethod
    def classify_similarity(score: float) -> str:
        """
        Classifies similarity score into academic integrity result categories.
        0-19%: Original
        20-39%: Low Similarity
        40-59%: Needs Review
        60-100%: Potential Plagiarism
        """
        if score < 20.0:
            return "Original"
        elif score < 40.0:
            return "Low Similarity"
        elif score < 60.0:
            return "Needs Review"
        else:
            return "Potential Plagiarism"

    @classmethod
    def run_check(cls, submission_id: int, db: Session, force_recheck: bool = False) -> PlagiarismReport:
        """
        Executes full plagiarism analysis pipeline for a submission against all existing database submissions.
        """
        start_time = time.time()

        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            raise ValueError(f"Submission with ID {submission_id} not found.")

        # Check if report already exists and force_recheck is False
        existing_report = db.query(PlagiarismReport).filter(PlagiarismReport.submission_id == submission_id).first()
        if existing_report and not force_recheck:
            return existing_report

        # 1. Ensure target document text is extracted
        target_text = submission.extracted_text
        if not target_text:
            try:
                extracted, w_count, c_count = extract_text_from_file(submission.file_path, submission.original_filename)
                submission.extracted_text = extracted
                db.commit()
                target_text = extracted
            except DocumentExtractionError as e:
                # If extraction fails, log and generate a 0% report with notification
                target_text = ""

        # Basic word count metrics
        tokens = tokenize_words(target_text, remove_stopwords=False)
        total_words = len(tokens)
        unique_words = len(set(tokens))

        if total_words < 5:
            # Document is too short or empty
            overall_score = 0.0
            result_label = "Original"
            processing_duration = round(time.time() - start_time, 3)

            # Delete old report if rechecking
            if existing_report:
                db.delete(existing_report)
                db.commit()

            report = PlagiarismReport(
                submission_id=submission.id,
                similarity_score=0.0,
                result=result_label,
                matched_documents_count=0,
                processing_time=processing_duration,
                total_words=total_words,
                total_unique_words=unique_words,
                method_summary=json.dumps({"method": "TF-IDF + Winnowing Fingerprinting", "status": "Insufficient text extracted"}),
                review_status="Pending Review"
            )
            db.add(report)
            submission.submission_status = "Checked"
            db.commit()
            db.refresh(report)
            return report

        # 2. Query corpus submissions (exclude the same submission)
        corpus_submissions = db.query(Submission).filter(
            Submission.id != submission.id,
            Submission.id < submission.id # Compare with previously submitted academic documents
        ).all()

        # If there are no earlier submissions, fallback to comparing against all other submissions
        if not corpus_submissions:
            corpus_submissions = db.query(Submission).filter(
                Submission.id != submission.id
            ).all()

        target_fingerprints = generate_fingerprints(target_text)
        
        valid_corpus_docs: List[Dict[str, Any]] = []
        corpus_texts: List[str] = []

        for c_sub in corpus_submissions:
            c_text = c_sub.extracted_text
            if not c_text and c_sub.file_path:
                try:
                    c_text, _, _ = extract_text_from_file(c_sub.file_path, c_sub.original_filename)
                    c_sub.extracted_text = c_text
                    db.commit()
                except Exception:
                    c_text = ""
            
            if c_text and len(tokenize_words(c_text)) >= 5:
                valid_corpus_docs.append({
                    "submission": c_sub,
                    "text": c_text,
                    "fingerprints": generate_fingerprints(c_text)
                })
                corpus_texts.append(c_text)

        matches_data = []

        if valid_corpus_docs and corpus_texts:
            # 3. Compute TF-IDF Cosine Similarities in batch
            tfidf_scores = compute_tfidf_similarities(target_text, corpus_texts)

            # 4. Compare with each corpus doc
            for idx, item in enumerate(valid_corpus_docs):
                c_sub = item["submission"]
                c_text = item["text"]
                c_fp = item["fingerprints"]

                tfidf_score = tfidf_scores[idx]
                fp_score = compute_jaccard_similarity(target_fingerprints, c_fp)

                # Compute hybrid similarity percentage
                score_pct = calculate_hybrid_score(tfidf_score, fp_score)

                # Only include matches with meaningful similarity (> 3%)
                if score_pct >= 3.0:
                    snippets = find_matching_snippets(target_text, c_text)
                    matches_data.append({
                        "matched_submission_id": c_sub.id,
                        "similarity_score": score_pct,
                        "matched_snippets": snippets
                    })

        # Sort matches by highest similarity score
        matches_data.sort(key=lambda x: x["similarity_score"], reverse=True)

        # 5. Determine overall similarity score
        if not matches_data:
            overall_score = 0.0
        else:
            # Top match is primary indicator; combined aggregate if multiple documents match
            top_score = matches_data[0]["similarity_score"]
            if len(matches_data) > 1:
                # Add small compounding factor for multi-source collation
                secondary_weight = sum(m["similarity_score"] for m in matches_data[1:4]) * 0.1
                overall_score = min(100.0, round(top_score + secondary_weight, 2))
            else:
                overall_score = top_score

        result_label = cls.classify_similarity(overall_score)
        processing_duration = round(time.time() - start_time, 3)

        # 6. Save or update report in DB
        if existing_report:
            db.delete(existing_report)
            db.commit()

        method_details = {
            "primary_method": "TF-IDF Vectorization with Cosine Similarity",
            "secondary_method": "K-Gram Fingerprinting with Winnowing",
            "phrase_matcher": "Exact and N-Gram Overlap Extraction",
            "corpus_size_checked": len(valid_corpus_docs),
            "top_match_score": matches_data[0]["similarity_score"] if matches_data else 0.0,
            "extensible_ai_module": "Ready for BERT/SentenceTransformer embedding integration"
        }

        report = PlagiarismReport(
            submission_id=submission.id,
            similarity_score=overall_score,
            result=result_label,
            matched_documents_count=len(matches_data),
            processing_time=processing_duration,
            total_words=total_words,
            total_unique_words=unique_words,
            method_summary=json.dumps(method_details),
            review_status="Pending Review"
        )
        db.add(report)
        db.flush()

        # Add match entries
        for match in matches_data:
            match_entry = SimilarityMatch(
                report_id=report.id,
                matched_submission_id=match["matched_submission_id"],
                similarity_score=match["similarity_score"],
                matched_text=json.dumps(match["matched_snippets"])
            )
            db.add(match_entry)

        # Update submission status
        submission.submission_status = "Checked"

        # Update project status if was just Submitted
        project = db.query(Project).filter(Project.id == submission.project_id).first()
        if project and project.status in ["Draft", "Submitted"]:
            project.status = "Under Review"

        # 7. Create notification for student
        notif = Notification(
            user_id=submission.submitted_by,
            title="Plagiarism Analysis Completed",
            message=f"Plagiarism check for '{submission.original_filename}' (v{submission.version}) finished with a similarity score of {overall_score}% ({result_label}).",
            type="info" if overall_score < 40.0 else "warning",
            link=f"/student/reports/{report.id}"
        )
        db.add(notif)

        # Notify supervisor if assigned
        if project and project.supervisor and project.supervisor.user_id:
            sup_notif = Notification(
                user_id=project.supervisor.user_id,
                title="New Submission Ready for Review",
                message=f"Student submitted '{submission.original_filename}' for project '{project.title}'. Similarity score: {overall_score}%.",
                type="info",
                link=f"/supervisor/reports"
            )
            db.add(sup_notif)

        # Audit log
        audit = AuditLog(
            user_id=submission.submitted_by,
            action="PLAGIARISM_CHECK",
            description=f"Generated plagiarism report #{report.id} for submission #{submission.id}. Similarity: {overall_score}% ({result_label})"
        )
        db.add(audit)

        db.commit()
        db.refresh(report)
        return report
