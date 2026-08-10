# ============================================================
# NexRay AI - Authentication Service
# This handles password hashing and JWT token creation
# and verification for doctor accounts.
# ============================================================

from passlib.context import CryptContext  # For hashing passwords
from jose import JWTError, jwt  # For creating and verifying JWT tokens
from datetime import datetime, timedelta  # For setting token expiry
from dotenv import load_dotenv
import os

load_dotenv()

# Secret key used to sign JWT tokens — stored in .env
SECRET_KEY = os.getenv("SECRET_KEY")

# Algorithm used to sign the token
ALGORITHM = "HS256"

# How long a token lasts before the doctor has to log in again
TOKEN_EXPIRE_HOURS = 24

# Password hashing context — uses bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # Takes a plain text password and returns a hashed version
    # We never store plain passwords in the database
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Checks if a plain password matches the stored hash
    # Returns True if they match, False if not
    return pwd_context.verify(plain_password, hashed_password)

def create_token(data: dict) -> str:
    # Creates a JWT token containing the doctor's info
    # The token expires after 24 hours
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})  # Add expiry time to the token
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    # Verifies a JWT token and returns the data inside it
    # Raises an error if the token is invalid or expired
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None