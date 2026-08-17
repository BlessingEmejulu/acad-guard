"""
Text Preprocessor for Plagiarism Detection.
Handles text cleaning, tokenization, normalization, and stop-word filtering.
"""
import re
import string
import unicodedata
from typing import List, Set

# Standard academic English stop-words
ACADEMIC_STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "cannot", "could", "couldn",
    "did", "didn", "do", "does", "doesn", "doing", "don", "down", "during", "each",
    "few", "for", "from", "further", "had", "hadn", "has", "hasn", "have", "haven",
    "having", "he", "her", "here", "hers", "herself", "him", "himself", "his",
    "how", "i", "if", "in", "into", "is", "isn", "it", "its", "itself", "let",
    "me", "more", "most", "mustn", "my", "myself", "no", "nor", "not", "of", "off",
    "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out",
    "over", "own", "same", "shan", "she", "should", "shouldn", "so", "some", "such",
    "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there",
    "these", "they", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn", "we", "were", "weren", "what", "when", "where", "which",
    "while", "who", "whom", "why", "with", "won", "would", "wouldn", "you", "your",
    "yours", "yourself", "yourselves"
}

def clean_text(text: str) -> str:
    """Normalize unicode characters, lower case, and collapse whitespace."""
    if not text:
        return ""
    # Normalize unicode (e.g. curly quotes, accented characters)
    text = unicodedata.normalize("NFKD", text)
    # Lowercase
    text = text.lower()
    # Replace newlines and tabs with single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def tokenize_words(text: str, remove_stopwords: bool = False) -> List[str]:
    """Tokenize clean text into alphanumeric words, optionally filtering stop words."""
    cleaned = clean_text(text)
    # Extract only alphanumeric tokens
    tokens = re.findall(r'\b[a-zA-Z0-9_]{2,}\b', cleaned)
    if remove_stopwords:
        tokens = [w for w in tokens if w not in ACADEMIC_STOP_WORDS]
    return tokens

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences for fine-grained phrase and snippet comparison."""
    if not text:
        return []
    # Match sentence boundaries (period, question mark, exclamation, or double newlines)
    raw_sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = []
    for s in raw_sentences:
        clean_s = s.strip()
        if len(clean_s) > 15: # Filter out single abbreviations
            sentences.append(clean_s)
    return sentences

def generate_ngrams(tokens: List[str], n: int = 3) -> List[str]:
    """Generate n-grams from a list of tokens."""
    if len(tokens) < n:
        return [" ".join(tokens)] if tokens else []
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]
