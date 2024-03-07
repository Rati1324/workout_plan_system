import os, json
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Header, Request
from sqlalchemy.orm import Session
from io import BytesIO
from typing import Optional

app = FastAPI()

@app.get("/")
def main():
    return {"result": "hi"}