from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import sqlite3
from datetime import datetime
import time
from database import get_db_connection
from schemas import TextInput, AnalysisOutput
from engine import mock_ai_engine
from fastapi.responses import RedirectResponse



app = FastAPI(
    title="NLP Insight API",
    description="Profesjonalne API do analizy sentymentu i klasyfikacji tekstu.",
    version="1.0.0"
)

# ENDPOINTS API
# przekierowanie na /docs
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.post("/analyze/", response_model=AnalysisOutput, tags=["AI Services"])
def analyze_text_endpoint(
    # input_data: tekst od użytkownika, ktory jest pilnowany dzieki TextInput zeby wygladal tak, a nie inaczej
    input_data: TextInput,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Główny endpoint. Przyjmuje tekst, przepuszcza przez model AI i loguje wynik.
    """
    # użycie "Mózgu" AI
    # .text tak jak w TextInput
    try:
        ai_result = mock_ai_engine(input_data.text)
        
        # o ktorej godzine zadano pytanie
        processing_time = datetime.now()

        # logowanie predykcji do bazy (MLOps)
        # cursor to taki "wskaźnik", którym pisze po bazie
        cursor = db.cursor()
        # wysyłam polecenie SQL
        # ?,? – to są bezpieczne miejsca, w które baza wstawi dane
        cursor.execute(
            """
            INSERT INTO predictions (input_text, source, sentiment, confidence, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (input_data.text, input_data.source, ai_result["sentiment"], ai_result["confidence"], processing_time)
        )
        # zapis zmiany
        db.commit()
        # baza danych informuje o tym, ze zapisała to pod numerem ... zapamiętuje ten numer, żeby oddać go użytkownikowi jako analysis_id
        new_id = cursor.lastrowid

        # zwrócenie ustrukturyzowanej odpowiedzi
        return AnalysisOutput(
            analysis_id=new_id,
            original_text_snippet=input_data.text[:50] + "...",
            sentiment=ai_result["sentiment"],
            confidence_score=ai_result["confidence"],
            detected_language=ai_result["language"],
            processed_at=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/monitoring/stats", tags=["MLOps Dashboard"])
def get_model_stats(db: sqlite3.Connection = Depends(get_db_connection)):
    """
    Endpoint, jak działa model na produkcji
    """
    cursor = db.cursor()
    # sprawdzam rozkład sentymentów
    cursor.execute("SELECT sentiment, COUNT(*) FROM predictions GROUP BY sentiment")

    # fetchall() zawsze zwraca listę krotek (list of tuples): [('POSITIVE', 5), ('NEGATIVE', 2), ('NEUTRAL', 1)]
    stats = dict(cursor.fetchall())
    
    # sprawdzam łączną ilość zapytań
    cursor.execute("SELECT COUNT(*) FROM predictions")

    # fetchone() zwraca dane w formacie krotki (tuple)
    total = cursor.fetchone()[0]

    return {
        "total_predictions": total,
        "sentiment_distribution": stats,
        "status": "Model healthy"
    }