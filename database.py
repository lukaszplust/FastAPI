import sqlite3
# BAZA DANYCH - logowanie zapytań MLOps
DB_NAME = "ai_logs.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_text TEXT,
                source TEXT,
                sentiment TEXT,
                confidence REAL,
                timestamp TEXT
            )
        """)
init_db()

# Dependency injection pattern
def get_db_connection():
    # tworze połączenie z plikiem na dysku
    conn = sqlite3.connect(DB_NAME)
    # używając yield tworze Context Manager
    # Nawet jeśli podczas analizy tekstu w endpoincie /analyze wydarzy się katastrofa i serwer wywali błąd (np. IndexError o którym rozmawialiśmy wcześniej),
    # Python i tak wróci do funkcji get_db_connection i wykona to, co jest po yield
    # Dzięki yield, funkcja "oddaje" połączenie do endpointu, ale czeka na boku, aż on skończy pracę, żeby potem wykonać sprzątanie.
    try:
        yield conn
    finally:
        conn.close()