import os, json
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Header, Request
from sqlalchemy.orm import Session
from io import BytesIO
from typing import Optional, List
from core.utils import get_db, get_hashed_password
from core.models import User
from core.config import Base, engine
from core.schemas import UserSchema
import re

app = FastAPI()
Base.metadata.create_all(bind=engine)

# @app.get("/", response_model=List[User])
@app.get("/")
def main(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.post("/register")
def register(user_data: UserSchema, db: Session = Depends(get_db)):
    password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
    username_regex = r"^(?=.*[a-zA-Z])(?=.*[\d\W]).{6,}$"

    if not re.match(password_regex, user_data.password):
        raise HTTPException(status_code=400, detail="Password is not secure")

    if not re.match(username_regex, user_data.username):
        raise HTTPException(status_code=400, detail="Your username must contain at least one letter, one number or special character, and be at least 6 characters long")

 
    hashed_password = get_hashed_password(user_data.password)

    db_user = User(
        username = user_data.username,
        password = hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
