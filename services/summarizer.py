import re
from collections import Counter
from typing import Dict, List

STOPWORDS = set([
    "the", "is", "was", "were", "are", "and", "or", "to", "of",
    "in", "that", "this", "with", "as", "for", "on", "at", "by",
    "an", "a", "from", "be", "been", "have", "has", "had", "it",
    "can", "will", "would", "could", "should", "do", "does", "did"
])

def sentence_score(sentence: str, keyword_freq: Counter) -> float:
    """Score a sentence based on keyword frequency"""
    words = re.findall(r"\w+", sentence.lower())
    if len(words) < 6:
        return 0
    score = sum(keyword_freq[w] for w in words if w not in STOPWORDS)
    return score / max(len(words), 1)

def extract_summary_paragraph(text: str) -> str:
    """Extract top 3-4 sentences into professional 2-3 line paragraph"""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    
    # Get keyword frequencies
    words = re.findall(r"\w+", text.lower())
    keywords = Counter(w for w in words if len(w) > 3 and w not in STOPWORDS)
    
    # Rank and select top sentences
    ranked = sorted(
        sentences,
        key=lambda s: sentence_score(s, keywords),
        reverse=True
    )
    
    # Take top 3-4 sentences
    top_sentences = []
    for s in ranked[:4]:
        s = s.strip()
        if len(s.split()) > 8 and s not in top_sentences:
            top_sentences.append(s)
    
    # Join into professional paragraph
    summary = " ".join(top_sentences)
    
    # Clean up extra dots/ellipsis
    summary = summary.rstrip('.')
    summary = summary.rstrip('…')
    summary = summary.rstrip('...')
    summary = summary.strip()
    
    return summary

def summarize_text(text: str) -> Dict:
    """Generate summary and structured transcription"""
    from services.transcriber import restore_punctuation, split_paragraphs
    
    cleaned = restore_punctuation(text)
    paragraphs = split_paragraphs(cleaned)
    
    # Create professional 2-3 line summary paragraph
    summary_paragraph = extract_summary_paragraph(cleaned)
    
    return {
        "full_transcription": paragraphs,
        "summary": {
            "paragraph": summary_paragraph
        }
    }
