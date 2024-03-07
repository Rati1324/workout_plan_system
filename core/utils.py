from .config import SessionLocal
from passlib.context import CryptContext
    
hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    return hash_context.hash(password)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()