import os, json
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Header, Request
from sqlalchemy.orm import Session
from io import BytesIO
from typing import Optional, List
from core.utils import get_db
from core.models import User
from core.config import Base, engine

app = FastAPI()
Base.metadata.create_all(bind=engine)

# @app.get("/", response_model=List[User])
@app.get("/")
def main(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.post("/register")