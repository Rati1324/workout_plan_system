import os
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from .config import SessionLocal
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt 
from dotenv import load_dotenv
from .models import User
from sqlalchemy.orm import Session

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
EXPIRATION_MINUTES = os.getenv("EXPIRATION_MINUTES")
    
hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
credential_exception = HTTPException(status_code=401, detail="Couldn't validate credentials")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_hashed_password(password: str) -> str:
    return hash_context.hash(password)

def create_jwt_token(sub: str):
    expire_mins = datetime.utcnow() + timedelta(minutes=int(EXPIRATION_MINUTES))
    data = {"username": sub, "exp": expire_mins}
    jwt_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_token

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")

        if payload["username"] is None:
            raise crendential_exception

        user = db.query(User).filter_by(username=username).first()
        if user is None:
            raise credential_exception
        return user
    except jwt.JWTError:
        raise credential_exception

