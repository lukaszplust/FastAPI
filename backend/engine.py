import time
def mock_ai_engine(text: str) -> dict:
    """
    Symuluje działanie modelu NLP. 
    Zwraca sentyment (POSITIVE/NEGATIVE/NEUTRAL) i pewność (confidence).
    """
    # symuluje opóźnienie prawdziwego modelu AI (np. 0.5 sekundy)
    time.sleep(0.5)
    
    text_lower = text.lower()
    if any(word in text_lower for word in ["świetna", "dobry", "polecam", "super", "great"]):
        return {"sentiment": "POSITIVE", "confidence": 0.95, "language": "pl"}
    elif any(word in text_lower for word in ["słaba", "błąd", "nie działa", "okropne", "bad"]):
        return {"sentiment": "NEGATIVE", "confidence": 0.88, "language": "pl"}
    else:
        return {"sentiment": "NEUTRAL", "confidence": 0.60, "language": "unk"}