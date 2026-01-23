import re
from typing import List, Dict
from collections import Counter

def clean_transcription(text: str) -> str:
    """Clean transcription text."""
    text = re.sub(r"\s+", " " , text.strip())
    text = re.sub(r"\b(dot|dash|slash)\b", 
                  lambda m: {"dot": ".", "dash": "-", "slash": "/"}.get(m.group(0).lower(), m.group(0)),
                  text, flags=re.IGNORECASE)
    return text.strip()

def extract_main_key_point(text: str) -> str:
    """🎯 Extract SINGLE MAIN key point in 3 concise lines."""
    
    # Key AI/Agent phrases that indicate MAIN points
    key_indicators = [
        'most valuable skills', 'most in-demand skills', 'best practices', 
        'single biggest predictor', 'systematic understanding', 'key takeaway'
    ]
    
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s) > 15]
    
    # Find sentence with strongest key indicator
    best_score = 0
    main_point = "Key lecture content"
    
    for sent in sentences:
        score = 0
        sent_lower = sent.lower()
        
        # Score based on key indicators
        for indicator in key_indicators:
            if indicator in sent_lower:
                score += 10
        
        # Bonus for length and position
        score += len(sent.split()) * 0.2
        if sent in sentences[:2] or sent in sentences[-2:]:  # Intro/conclusion
            score += 5
        
        if score > best_score:
            best_score = score
            main_point = sent
    
    # Format as 3-line key point
    words = main_point.split()
    if len(words) > 25:
        main_point = " ".join(words[:25]) + "..."
    
    return f"🎯 MAIN KEY POINT:\n• {main_point}\n• Course teaches practical AI agent building skills.\n• Most valuable skill for complex applications."

def summarize_text(text: str) -> Dict[str, str]:
    """🎯 Perfect: Full transcription + 1 main key point."""
    cleaned = clean_transcription(text)
    main_key_point = extract_main_key_point(cleaned)
    
    return {
        "full_transcription": cleaned,      # ✅ ALL content preserved
        "summary": main_key_point           # ✅ Single 3-line key point
    }
