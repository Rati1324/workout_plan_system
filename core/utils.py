import os
from .config import SessionLocal
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt 
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
EXPIRATION_MINUTES = os.getenv("EXPIRATION_MINUTES")
    
hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    return hash_context.hash(password)

def create_jwt_token(sub: str):
    expire_mins = datetime.utcnow() + timedelta(minutes=int(EXPIRATION_MINUTES))
    data = {"username": sub, "exp": expire_mins}
    jwt_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_token

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()