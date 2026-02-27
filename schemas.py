from pydantic import BaseModel, Field
from datetime import datetime
# Request
# definiuje schemat. Mówie FastAPI: „Każde zapytanie, które przyjdzie do mojego modelu AI, musi wyglądać dokładnie tak
class TextInput(BaseModel):
    # it must be a text
    text: str = Field(
        # field is needed
        ..., 
        min_length=5, 
        max_length=500, 
        description="Tekst do analizy (min 5 znaków)",
        example="Ta nowa funkcja w aplikacji jest naprawdę świetna, polecam!"
    )
    # if user didn't set any information system will use unknown
    source: str = Field("unknown", example="mobile_app_review")

# Response
class AnalysisOutput(BaseModel):
    analysis_id: int
    original_text_snippet: str
    sentiment: str
    confidence_score: float
    detected_language: str
    processed_at: datetime