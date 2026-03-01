from fastapi.testclient import TestClient
from main import app

# tworze klienta testowego
client = TestClient(app)

def test_analyze_positive():
    """Testing positive sentiment"""
    payload = {
        "text": "Working great",
        "source": "manual_test"
    }
    # communicate inside RAM
    # weź słownik o nazwie payload, zamień go na format tekstowy JSON i wsadź go do body (ciała) zapytania
    response = client.post("/analyze/", json=payload)
    
    # jeśli to, co jest po assert, okaże się nieprawdą, test świeci się na czerwono

    # sprawdzam, czy serwer w ogóle przeżył.
    # jeśli np. zapomniałem przecinka w kodzie i serwer wywalił błąd 500, ten test od razu o tym poinformuje.
    assert response.status_code == 200
    # wyciągam to, co API „odpowiedziało” w formacie JSON, żeby móc do tego zajrzeć
    data = response.json()
    # sprawdzam, czy model (engine.py) faktycznie rozpoznał słowo "great" jako pozytywne
    assert data["sentiment"] == "POSITIVE"
    # skoro w odpowiedzi jest analysis_id, to znaczy, że rekord został zapisany w SQLite i baza zwróciła numer ID
    assert "analysis_id" in data

def test_analyze_negative():
    """Testing negative sentiment."""
    payload = {
        "text": "Working bad",
        "source": "manual_test"
    }
    response = client.post("/analyze/", json=payload)
    
    assert response.status_code == 200
    assert response.json()["sentiment"] == "NEGATIVE"

def test_text_too_short():
    """Testing Pydantic validation - text must have min. 5 char."""
    payload = {
        "text": "Not",
        "source": "test"
    }
    response = client.post("/analyze/", json=payload)
    
    # waiting for error 422 (Unprocessable Entity) due to validation TextInput
    assert response.status_code == 422

def test_monitoring_stats():
    """Testing if stat endpoint returns valid data."""
    response = client.get("/monitoring/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert "total_predictions" in data
    assert "status" in data
    assert data["status"] == "Model healthy"