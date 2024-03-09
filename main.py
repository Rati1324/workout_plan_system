import json
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Header, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.utils import get_db, get_hashed_password, create_jwt_token, get_current_user
from core.models import User, Excercise, WorkoutPlan
from core.config import Base, engine
from core.schemas import UserSchema, WorkoutPlanSchema
import re
from seed_db import seed, clear

app = FastAPI()
Base.metadata.create_all(bind=engine)

# seed()
# clear()
@app.get("/")
async def main(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.post("/register")
async def register(user_data: UserSchema, db: Session = Depends(get_db)):
    password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"

    if not re.match(password_regex, user_data.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter, one uppercase letter, one digit, and be at least 8 characters long")

    if len(user_data.username) < 6:
        raise HTTPException(status_code=400, detail="Username must be over 6 characters long")
 
    hashed_password = get_hashed_password(user_data.password)

    db_user = User(
        username = user_data.username,
        password = hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    token = create_jwt_token(user_data.username)
    return {"response": token}

@app.post("/login")
async def login(db: Session = Depends(get_db), user_data: OAuth2PasswordRequestForm = Depends()):
    print(user_data)
    user = db.query(User).filter_by(username=user_data.username).first()
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")

    hashed_password = get_hashed_password(user_data.password)

    if not hashed_password != user.password:
        raise HTTPException(status_code=400, detail="Invalid password")
    token = create_jwt_token(user_data.username)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/get_excercises")
async def get_excercises(dependencies = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Excercise).all()

@app.post("/create_plan")
async def create_plan(dependencies = Depends(get_current_user), db: Session = Depends(get_db), workout_plan: WorkoutPlanSchema = None):
    print(dependencies)
    print(workout_plan)
    # get_current_user(db, token)
    return {"response": "hi"}