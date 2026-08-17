"""
Plagiarism detection package exports.
"""
from app.services.plagiarism.preprocessor import clean_text, tokenize_words, split_into_sentences
from app.services.plagiarism.fingerprinting import generate_fingerprints, compute_jaccard_similarity, find_matching_snippets
from app.services.plagiarism.vectorizer import compute_tfidf_similarities, calculate_hybrid_score
from app.services.plagiarism.engine import PlagiarismEngine

__all__ = [
    "clean_text",
    "tokenize_words",
    "split_into_sentences",
    "generate_fingerprints",
    "compute_jaccard_similarity",
    "find_matching_snippets",
    "compute_tfidf_similarities",
    "calculate_hybrid_score",
    "PlagiarismEngine"
]
