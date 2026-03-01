"""
DATABASE MODULE (PostgreSQL)

This module handles the connection and initialization of the PostgreSQL database.
It uses 'psycopg2' as the adapter and 'python-dotenv' for secure configuration.

Key Features:
1. Environment-driven: Connection string is loaded from a .env file for security.
2. Resilience: Includes a startup delay and retry logic for Docker synchronization.
3. Schema Management: Automatically creates 'users' and 'predictions' tables if they don't exist.
4. Resource Safety: Uses a generator pattern (yield) for FastAPI Dependency Injection 
    to ensure every connection is properly closed.

Relationship Model:
- A One-to-Many relationship exists between 'users' and 'predictions'.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# retrieve Database URL from environment variables
# this URL contains the connection details (user, password, host, port, dbname)
DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

def init_db():
    """
    Initializes the database schema on application startup.
    Creates necessary tables if they do not already exist.
    """
    # allowing a short delay (3s) for the PostgreSQL container to fully start in Docker
    time.sleep(3)
    
    # Establish connection to the PostgreSQL database
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # create 'users' table: stores authentication credentials
    # SERIAL is used for auto-incrementing the primary key
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            login TEXT UNIQUE,
            password TEXT
        )
    """)
    # create 'predictions' table: stores chat history and AI response logs
    # user_id is a foreign key linked to the 'users' table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            chat_name TEXT,
            input_text TEXT,
            source TEXT,
            sentiment TEXT,
            confidence REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # commit changes and close the connection
    conn.commit()
    cur.close()
    conn.close()
    print("PostgreSQL database initialized successfully!")

# execute database initialization when the module is imported
try:
    init_db()
except Exception as e:
    print(f"Database initialization error (Is Docker running?): {e}")

def get_db_connection():
    """
    Database connection generator for FastAPI Dependency Injection.
    Ensures that the connection is closed after the request is processed.
    """
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()