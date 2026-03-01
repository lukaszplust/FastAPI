'''
Hash: jednokierunkowa funkcja matematyczna. Nie da się "odkodować" hasha z powrotem na hasło. Można tylko sprawdzić, czy dwa hasła dają ten sam hash.

JWT (JSON Web Token): Kompaktowy sposób bezpiecznego przesyłania informacji między stronami (React <-> FastAPI).
Składa się z trzech części: nagłówka, ładunku (payload) i podpisu.

Payload: "Ładunek" tokenu. Tam zapisuje user_id i exp (expiration).

Signature: Podpis. Tworzony na podstawie SECRET_KEY. Gwarantuje, że nikt nie zmienił danych w tokenie (np. nie zmienił user_id na ID admina).

Claims: To poszczególne pola wewnątrz tokenu, takie jak exp (czas wygaśnięcia) czy sub (identyfikator użytkownika).
'''
"""-----------------------------------------"""


"""
AUTHENTICATION & SECURITY MODULE

This module handles user security, password hashing, and JWT (JSON Web Token) management.

Architecture:
- Hashing: Uses 'bcrypt' via Passlib for one-way secure password storage.
- Authorization: Implements JWT for stateless authentication between React and FastAPI.
- Security: Uses a SECRET_KEY signed signature to ensure data integrity within tokens.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
# jose (python-jose): biblioteka do obsługi tokenów JWT. To ona pakuje dane użytkownika w zaszyfrowany sznurek znaków
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# load environment variables from the .env file
load_dotenv()

# password hashing configuration using the bcrypt algorithm
# cryptContext handles password hashing and verification logic
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration settings retrieved from environment variables
# SECRET_KEY is used to sign the tokens (critical for security)
SECRET_KEY = os.getenv("SECRET_KEY") 
ALGORITHM = os.getenv("ALGORITHM", "HS256")
# convert string from .env to integer, default to 60 minutes
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# funkcja do hashowania hasła (przy rejestracji)
def get_password_hash(password):
    """
    Generates a secure hash from a plain-text password.
    Used during user registration.
    """
    return pwd_context.hash(password)

# funkcja do sprawdzania czy hasło pasuje (przy logowaniu)
def verify_password(plain_password, hashed_password):
    """
    Compares a plain-text password with a stored hash to check for a match.
    Used during user login.
    """
    return pwd_context.verify(plain_password, hashed_password)

# funkcja tworząca Token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Generates a JSON Web Token (JWT) for user authentication.
    The token contains user data and an expiration timestamp.
    """

    to_encode = data.copy()
    
    # set the expiration time for the token
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        # use the default expiration time from settings
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # adding the expiration ('exp') claim to the token payload
    to_encode.update({"exp": expire})
    # sign and encode the JWT using the secret key and specified algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt