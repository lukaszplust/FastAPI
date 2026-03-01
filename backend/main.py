from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import psycopg2
from datetime import datetime, timedelta
import time
from database import get_db_connection
from schemas import TextInput, AnalysisOutput, UserAuth, UserResponse
from engine import mock_ai_engine
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from auth import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from auth import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(
    title="NLP Insight API",
    description="Profesjonalne API do analizy sentymentu (PostgreSQL Edition).",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user_id(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Nie udało się zweryfikować uprawnień",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return int(user_id) 
    except JWTError:
        raise credentials_exception

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.post("/analyze/", response_model=AnalysisOutput, tags=["AI Services"])
def analyze_text_endpoint(
    input_data: TextInput,
    chat_name: str, 
    db = Depends(get_db_connection),
    current_user_id: int = Depends(get_current_user_id)
):
    try:
        ai_result = mock_ai_engine(input_data.text)
        processing_time = datetime.now()
        cursor = db.cursor()

        #  dodanie RETURNING id, żeby pobrać numer wpisu
        cursor.execute(
            """
            INSERT INTO predictions (user_id, chat_name, input_text, source, sentiment, confidence, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (current_user_id, chat_name, input_data.text, input_data.source, ai_result["sentiment"], ai_result["confidence"], processing_time)
        )
        
        # W Postgresie ID pobieramy przez fetchone() po RETURNING
        new_id = cursor.fetchone()[0]
        db.commit()

        return AnalysisOutput(
            analysis_id=new_id,
            original_text_snippet=input_data.text[:50],
            sentiment=ai_result["sentiment"],
            confidence_score=ai_result["confidence"],
            detected_language=ai_result["language"],
            processed_at=processing_time
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/monitoring/stats", tags=["MLOps Dashboard"])
def get_model_stats(db = Depends(get_db_connection)):
    cursor = db.cursor()
    cursor.execute("SELECT sentiment, COUNT(*) FROM predictions GROUP BY sentiment")
    stats = dict(cursor.fetchall())
    
    cursor.execute("SELECT COUNT(*) FROM predictions")
    total = cursor.fetchone()[0]

    return {
        "total_predictions": total,
        "sentiment_distribution": stats,
        "status": "Model healthy"
    }

# --- ENDPOINTY LOGOWANIA ---

@app.post("/register", tags=["Auth"])
def register_user(user_data: UserAuth, db = Depends(get_db_connection)):
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM users WHERE login = %s", (user_data.login,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="User already exist !")
    
    hashed_password = pwd_context.hash(user_data.password)
    
    try:
        cursor.execute(
            "INSERT INTO users (login, password) VALUES (%s, %s)",
            (user_data.login, hashed_password)
        )
        db.commit()
        return {"message": "Zarejestrowano pomyślnie!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Błąd zapisu do bazy.")

@app.post("/login", tags=["Auth"])
def login_user(user_data: UserAuth, db = Depends(get_db_connection)):
    cursor = db.cursor()
    
    cursor.execute("SELECT id, login, password FROM users WHERE login = %s", (user_data.login,))
    user = cursor.fetchone() 
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid login or password")
    
    if not pwd_context.verify(user_data.password, user[2]):
        raise HTTPException(status_code=401, detail="Invalid login or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": str(user[0])},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "login": user[1]
    }

@app.get("/history", tags=["User Data"]) 
def get_user_history(
    db = Depends(get_db_connection),
    current_user_id: int = Depends(get_current_user_id)
):
    cursor = db.cursor()
    cursor.execute(
        "SELECT input_text, sentiment, chat_name FROM predictions WHERE user_id = %s ORDER BY timestamp ASC", 
        (current_user_id,)
    )
    rows = cursor.fetchall()
    return [{"text": r[0], "sentiment": r[1], "chat_name": r[2]} for r in rows]

@app.delete("/chat/{chat_name}", tags=["User Data"])
def delete_chat(
    chat_name: str, 
    db = Depends(get_db_connection), 
    current_user_id: int = Depends(get_current_user_id)
):
    try:
        cursor = db.cursor()
        # usuwam z tabeli 'predictions', bo tam trzymam historię
        cursor.execute(
            "DELETE FROM predictions WHERE user_id = %s AND chat_name = %s",
            (current_user_id, chat_name)
        )
        db.commit()
        
        # Jeśli nic nie usunięto, można opcjonalnie rzucić błąd, 
        # ale zazwyczaj zwraca się sukces, bo cel został osiągnięty (czatu nie ma)
        return {"status": "success", "message": f"Chat '{chat_name}' deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Błąd podczas usuwania: {str(e)}")