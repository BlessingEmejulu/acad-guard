"""
Fingerprinting and Exact Phrase Matching for Plagiarism Detection.
Implements K-gram hashing and sentence-level similarity extraction.
"""
import hashlib
from typing import List, Set, Dict, Tuple
from app.services.plagiarism.preprocessor import clean_text, tokenize_words, split_into_sentences, generate_ngrams

def hash_kgram(kgram: str) -> int:
    """Create a 64-bit integer hash for a k-gram string."""
    return int(hashlib.md5(kgram.encode("utf-8")).hexdigest()[:16], 16)

def generate_fingerprints(text: str, k: int = 5, window_size: int = 4) -> Set[int]:
    """
    Generate document fingerprints using the Winnowing algorithm.
    - k: k-gram token size (default: 5 tokens)
    - window_size: sliding window size for local minimum selection
    """
    tokens = tokenize_words(text, remove_stopwords=False)
    if not tokens:
        return set()
    
    kgrams = generate_ngrams(tokens, n=k)
    hashes = [hash_kgram(kg) for kg in kgrams]

    if not hashes:
        return set()

    if len(hashes) <= window_size:
        return {min(hashes)}

    fingerprints = set()
    min_idx = -1
    for i in range(len(hashes) - window_size + 1):
        window = hashes[i:i + window_size]
        min_val = min(window)
        # Select the rightmost minimum
        current_min_idx = i + [j for j, val in enumerate(window) if val == min_val][-1]
        if current_min_idx != min_idx:
            min_idx = current_min_idx
            fingerprints.add(min_val)

    return fingerprints

def compute_jaccard_similarity(set_a: Set[int], set_b: Set[int]) -> float:
    """Compute Jaccard similarity coefficient between two sets of fingerprints."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    if union == 0:
        return 0.0
    return float(intersection / union)

def find_matching_snippets(source_text: str, target_text: str, min_match_words: int = 6) -> List[str]:
    """
    Identify matching sentences or overlapping phrases between source and target text.
    Returns a list of clean matched excerpts.
    """
    source_sentences = split_into_sentences(source_text)
    target_clean = clean_text(target_text)
    
    matched_snippets = []
    
    for sent in source_sentences:
        clean_sent = clean_text(sent)
        sent_tokens = tokenize_words(clean_sent, remove_stopwords=False)
        
        if len(sent_tokens) < min_match_words:
            continue
            
        # Check if 6-gram or whole sentence appears in target text
        if clean_sent in target_clean:
            matched_snippets.append(sent)
            continue
            
        # Check 5-gram chunks
        chunks = generate_ngrams(sent_tokens, n=min_match_words)
        for chunk in chunks:
            if chunk in target_clean:
                matched_snippets.append(sent)
                break
                
        if len(matched_snippets) >= 8: # Limit to top 8 distinct snippets for UI readability
            break

    return matched_snippets
