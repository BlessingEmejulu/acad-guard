"""
TF-IDF Vectorization and Cosine Similarity calculation for Academic Plagiarism Detection.
"""
from typing import List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.services.plagiarism.preprocessor import clean_text, ACADEMIC_STOP_WORDS

def compute_tfidf_similarities(query_text: str, corpus_texts: List[str]) -> List[float]:
    """
    Compute cosine similarity between a single query document and a list of corpus documents.
    Returns a list of similarity scores (0.0 to 1.0) corresponding to each corpus item.
    """
    if not query_text or not corpus_texts:
        return [0.0] * len(corpus_texts)

    # Clean all texts
    clean_query = clean_text(query_text)
    clean_corpus = [clean_text(doc) for doc in corpus_texts]

    # Combine for unified vocabulary fitting
    all_documents = [clean_query] + clean_corpus

    try:
        vectorizer = TfidfVectorizer(
            stop_words=list(ACADEMIC_STOP_WORDS),
            ngram_range=(1, 2), # Unigrams and bigrams
            sublinear_tf=True,
            max_df=0.95,
            min_df=1
        )
        tfidf_matrix = vectorizer.fit_transform(all_documents)
        
        # Query is index 0, corpus is indices 1..N
        query_vector = tfidf_matrix[0:1]
        corpus_vectors = tfidf_matrix[1:]
        
        cosine_scores = cosine_similarity(query_vector, corpus_vectors)[0]
        return [float(score) for score in cosine_scores]
    except Exception:
        # Fallback to simple token overlap if vocabulary is too sparse
        query_words = set(clean_query.split())
        scores = []
        for doc in clean_corpus:
            doc_words = set(doc.split())
            if not query_words or not doc_words:
                scores.append(0.0)
            else:
                overlap = len(query_words.intersection(doc_words)) / max(len(query_words), len(doc_words))
                scores.append(float(overlap))
        return scores

def calculate_hybrid_score(tfidf_score: float, fingerprint_score: float) -> float:
    """
    Combine TF-IDF cosine similarity and fingerprint Jaccard overlap into a unified percentage (0 - 100%).
    Takes weighted combination while respecting high verbatim overlap.
    """
    # If fingerprint overlap is very high (direct verbatim copy), prioritize it
    if fingerprint_score > 0.6:
        combined = (0.35 * tfidf_score) + (0.65 * fingerprint_score)
    else:
        combined = (0.70 * tfidf_score) + (0.30 * fingerprint_score)

    percentage = round(min(1.0, max(0.0, combined)) * 100.0, 2)
    return percentage
