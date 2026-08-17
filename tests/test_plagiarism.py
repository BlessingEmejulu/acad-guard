"""
Unit tests for Plagiarism Engine NLP algorithms.
"""
from app.services.plagiarism.preprocessor import clean_text, tokenize_words, split_into_sentences
from app.services.plagiarism.fingerprinting import generate_fingerprints, compute_jaccard_similarity, find_matching_snippets
from app.services.plagiarism.vectorizer import compute_tfidf_similarities, calculate_hybrid_score
from app.services.plagiarism.engine import PlagiarismEngine

def test_text_preprocessing():
    raw = "Artificial   Intelligence   in Healthcare: An Overview! \n\n New paragraph."
    cleaned = clean_text(raw)
    assert "artificial intelligence in healthcare" in cleaned
    
    tokens = tokenize_words(raw, remove_stopwords=True)
    assert "artificial" in tokens
    assert "in" not in tokens # Stop-word filtered
    assert "an" not in tokens

def test_identical_document_plagiarism():
    text_a = "Cloud computing infrastructures have become pivotal targets for distributed cyber attacks."
    text_b = "Cloud computing infrastructures have become pivotal targets for distributed cyber attacks."
    
    fp_a = generate_fingerprints(text_a)
    fp_b = generate_fingerprints(text_b)
    jaccard = compute_jaccard_similarity(fp_a, fp_b)
    assert jaccard > 0.8 # High identical overlap

    scores = compute_tfidf_similarities(text_a, [text_b])
    assert scores[0] > 0.95 # Highly identical TF-IDF cosine score

    hybrid = calculate_hybrid_score(scores[0], jaccard)
    assert hybrid >= 90.0

def test_dissimilar_documents_low_score():
    text_a = "Deep convolutional neural networks perform visual feature extraction on cassava plant leaves."
    text_b = "Decentralized zero-knowledge rollup smart contracts execute on Ethereum blockchain."
    
    fp_a = generate_fingerprints(text_a)
    fp_b = generate_fingerprints(text_b)
    jaccard = compute_jaccard_similarity(fp_a, fp_b)
    assert jaccard == 0.0

    scores = compute_tfidf_similarities(text_a, [text_b])
    assert scores[0] < 0.15 # Very low similarity

def test_snippet_matching():
    source = "Network intrusion detection systems inspect packet telemetry in software-defined hypervisors to mitigate attacks."
    target = "Our approach is unique because network intrusion detection systems inspect packet telemetry in software-defined hypervisors to mitigate attacks effectively."
    
    snippets = find_matching_snippets(source, target, min_match_words=5)
    assert len(snippets) > 0
    assert "network intrusion detection systems" in snippets[0].lower()

def test_classification_ranges():
    assert PlagiarismEngine.classify_similarity(10.5) == "Original"
    assert PlagiarismEngine.classify_similarity(25.0) == "Low Similarity"
    assert PlagiarismEngine.classify_similarity(45.0) == "Needs Review"
    assert PlagiarismEngine.classify_similarity(85.0) == "Potential Plagiarism"
